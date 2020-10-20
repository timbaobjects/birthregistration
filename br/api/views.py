# -*- coding: utf-8 -*-
from django.db import connection
from django.http import JsonResponse
from django.utils.timezone import now

from br.api.utils import get_api_data
from br.models import CensusResult
from br.utils import extract_reporting_records
from locations.models import Location


def dashboard(request):
    level = request.GET.get('level', 'country')
    try:
        year = int(request.GET.get('year'))
    except TypeError, ValueError:
        year = None
    try:
        month = int(request.GET.get('month'))
    except TypeError, ValueError:
        month = None

    return JsonResponse(get_api_data(level, year, month))


def get_projection_data(request):
    current_timestamp = now()
    cursor = connection.cursor()
    cursor.execute('SELECT MIN(time), MAX(time) FROM br_birthregistration')
    result = cursor.fetchone()
    min_time, max_time = result if result else (current_timestamp, current_timestamp)

    # extract location
    location_id = request.GET.get('location')
    try:
        location = Location.objects.get(pk=location_id)
    except Exception:
        return JsonResponse(dict(message='Location not found', status='error'), status=404)

    # extract year
    try:
        year = int(request.GET.get('year'))
        if year < min_time.year or year > max_time.year:
            return JsonResponse(dict(message='Invalid year', status='error'), status=400)
    except TypeError, ValueError:
        year = current_timestamp.year

    # extract month
    month_raw = request.GET.get('month')
    if month_raw is None:
        month = None
    else:
        try:
            month = int(month_raw)
        except ValueError:
            month = current_timestamp.month
    if month is not None:
        if month < 1 or month > 12:
            return JsonResponse(dict(message='Invalid month', status='error'), status=400)

    reporting_df, prior_u1_df = extract_reporting_records(location, year, month)
    census_result = CensusResult.get_estimate_dataframe(year, month).reset_index()

    if location.level == 0:
        group_columns = ['state', 'state_id']
    elif location.level == 2:
        group_columns = ['lga', 'lga_id']
    else:
        return JsonResponse(dict(message='Invalid location specified', status='error'), status=400)

    summed_reporting_df = reporting_df.groupby(
        group_columns).sum().reset_index()
    summed_prior_u1_df = prior_u1_df.groupby(
        group_columns[1]).sum().reset_index()

    combined_df = summed_reporting_df.merge(
        summed_prior_u1_df, on=group_columns[1], suffixes=('', '_prior')
    ).merge(
        census_result, left_on=group_columns[1], right_on='loc_id'
    )

    return JsonResponse(dict(data=combined_df.to_dict(orient='records'), status='ok'))
