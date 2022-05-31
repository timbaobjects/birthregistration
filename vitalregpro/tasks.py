# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import re

from celery import shared_task
from django.utils.timezone import get_current_timezone, now
from fuzzywuzzy import process

from br.models import BirthRegistration
from common.constants import DATA_SOURCE_EXTERNAL, DATA_SOURCE_INTERNAL
from locations.models import Facility, Location, LocationType
from vitalregpro.client.crvs import CRVSClient


def _preprocess_name(name):
    '''
    Performs preprocessing on names to ease matching.
    
    Replace stop words like 'health centre' and 'hospital'
    with equivalents that make it easy to do fuzzy matching
    '''
    sub = re.sub('primary health centre', 'PHC', name, flags=re.I)
    sub = re.sub('primary health center', 'PHC', sub, flags=re.I)
    sub = re.sub('health center', 'HC', sub, flags=re.I)
    sub = re.sub('health centre', 'HC', sub, flags=re.I)
    sub = re.sub('hospital', 'Hosp', sub, flags=re.I)

    return sub


def _resolve_centre(centre_info):
    centre_id = centre_info.get('id')
    name = centre_info.get('name')
    lga_id = centre_info.get('lga')
    state_id = centre_info.get('state')

    def _create_centre():
        location_type = LocationType.objects.get(name='RC')
        lga = Location.objects.get(vrp_id=lga_id, type__name='LGA')
        last_rc_code = lga.children.filter(type__name=u'RC').order_by(
            u'-code').first().code
        try:
            next_rc_code = str(int(last_rc_code) + 1).zfill(9)
        except ValueError:
            raise
        centre = Location.objects.create(
            name=name, parent=lga, vrp_id=centre_id, type=location_type,
            source=DATA_SOURCE_EXTERNAL, code=next_rc_code)
        Facility.objects.create(name=name, code=next_rc_code, location=centre)

        return centre

    # check if centre has been saved and matched
    query = Location.objects.filter(
        vrp_id=centre_id, parent__vrp_id=lga_id,
        parent__parent__vrp_id=state_id,
    )
    if query.exists():
        return query.first()

    # use the FTS for the centre name, and filter
    # by the state and LGA VRP IDs too
    results = Location.objects.filter(
        name__search=name, parent__vrp_id=lga_id,
        parent__parent__vrp_id=state_id, type__name='RC', vrp_id=None
    )

    # no match, create the centre and return it
    if not results.exists():
        return _create_centre()

    # get the closest possible match with a cutoff of 70
    preprocessed_name = _preprocess_name(name)
    names = results.values_list('name', flat=True)
    preprocessed_names = [_preprocess_name(n) for n in names]
    names_map = {pn: n for n, pn in zip(names, preprocessed_names)}
    process_result = process.extractOne(
        preprocessed_name, preprocessed_names, score_cutoff=70)
    if process_result is None:
        return _create_centre()
    top_name, _ = process_result

    centre = results.get(name=names_map[top_name])
    centre.vrp_id = centre_id
    centre.save()

    return centre


def _post_births(aggregate_records, report_date):
    for centre_id, record in aggregate_records.items():
        centre_data = record.get('meta').copy()
        centre_data.update(id=centre_id)
        centre = _resolve_centre(centre_data)

        # convert report date to midnight in app time zone
        report_date = report_date.astimezone(
            get_current_timezone()
        ).replace(hour=0, minute=0, second=0, microsecond=0)

        try:
            query = BirthRegistration.objects.filter(
                location=centre, time=report_date)
            br_report = query.get(source=DATA_SOURCE_EXTERNAL)
            sms_reports = query.exclude(source=DATA_SOURCE_INTERNAL)
            if sms_reports.exists():
                sms_reports.update(disabled=True)
        except BirthRegistration.DoesNotExist:
            br_report = BirthRegistration(
                location=centre, source=DATA_SOURCE_EXTERNAL, time=report_date)

        br_report.boys_below1 = record.get('Male').get('U1')
        br_report.boys_1to4 = record.get('Male').get('1-4')
        br_report.boys_5to9 = record.get('Male').get('5-9')
        br_report.boys_10to18 = record.get('Male').get('10+')
        br_report.girls_below1 = record.get('Female').get('U1')
        br_report.girls_1to4 = record.get('Female').get('1-4')
        br_report.girls_5to9 = record.get('Female').get('5-9')
        br_report.girls_10to18 = record.get('Female').get('10+')
        br_report.save()


def _remote_sync(date_string):
    '''
    syncs centres and birth records from VRP REST API
    Arguments:
    - date_string: date string in YYYY-MM-DD format
    '''
    client = CRVSClient()
    client.authenticate()

    birth_records = client.get_births(date_string)
    if len(birth_records) > 0:
        aggregate_records, report_date = client.collate_records(birth_records)
        _post_births(aggregate_records, report_date)

    client.logout()


@shared_task
def sync_from_remote(date_string=None):
    if date_string is None:
        date_string = now().strftime('%Y-%m-%d')
    _remote_sync(date_string)
