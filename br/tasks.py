from __future__ import absolute_import

import calendar
from datetime import datetime
from operator import itemgetter

from celery import shared_task
from dateutil.relativedelta import relativedelta
from django.db import connection as db_connection
from django.core import mail
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import make_aware, now
from rapidsms.contrib.messagelog.models import Message
from rapidsms.models import Connection
import pandas as pd

from br.models import BirthRegistration, CensusResult, Subscription
from br.raw_queries import CENTRE_REPORTING_QUERY, DATA_QUERY, PRIOR_DATA_QUERY
from br.utils import generate_report_attachment
from locations.models import Location
from messaging.utils import send_sms_message


def beginning_of_the_month(dt):
    return make_aware(datetime(dt.year, dt.month, 1))


def end_of_the_month(dt):
    if dt.month == 12: # if the month is December, then return Jan. 1 of the next year
        return make_aware(datetime(dt.year + 1, 1, 1))
    else: # if not, subtract one second from the next month
        return make_aware(
            datetime(dt.year, dt.month + 1, 1)) - relativedelta(seconds=1)


@shared_task
def mid_month_reports():
    timestamp = now()
    template_name = 'email/reporting_report.html'

    dataset = compute_reporting(timestamp)
    for subscription in Subscription.objects.all():
        user = subscription.subscriber
        if not user.email:
            continue

        for location in subscription.locations.all():
            location_data = dataset.get(location.pk)
            if location_data is None:
                continue
            context = {
                'location': location.name,
                'location_type': location.type.name,
                'month': calendar.month_name[timestamp.month],
                'year': timestamp.year,
                'report': location_data
            }
            message_body = render_to_string(template_name, context)
            send_mail(
                'Birth Registration Reporting Summary', '',
                settings.DEFAULT_FROM_EMAIL, [user.email],
                html_message=message_body)


@shared_task
def monthly_reports():
    timestamp = now()
    template_name = 'email/monthly_report.html'

    # get the dates for a month previous and the current
    reporting_date = timestamp + relativedelta(months=-1)
    prior_date = timestamp + relativedelta(months=-2)

    # generate reports
    recent_report = compute_reports(reporting_date.year, reporting_date.month)
    prior_report = compute_reports(prior_date.year, prior_date.month)

    # email the relevant portions
    with mail.get_connection() as mail_connection:
        for subscription in Subscription.objects.all():
            user = subscription.subscriber
            if not user.email:
                continue

            for location in subscription.locations.filter(
                            type__name__in=['Country', 'State']):
                recent_data = recent_report.get(location.pk)
                prior_data = prior_report.get(location.pk)

                if recent_data is None or prior_data is None:
                    continue

                context = {
                    'month': calendar.month_name[reporting_date.month],
                    'year': reporting_date.year,
                    'prev_month': calendar.month_name[prior_date.month],
                    'prev_year': prior_date.year,
                    'report': recent_data,
                    'prev_report': prior_data,
                    'location': location.name,
                    'location_type': location.type.name,
                }

                message = mail.EmailMessage(
                    subject='Birth Registration Monthly Summary',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                    body=render_to_string(template_name, context),
                    connection=mail_connection)
                message.content_subtype = 'html'
                message.attach(
                    'monthly_report.csv',
                    generate_report_attachment(recent_data), 'text/csv')
                message.attach(
                    'previous_monthly_report.csv',
                    generate_report_attachment(prior_data), 'text/csv')
                message.send()


@shared_task
def mid_month_reports():
    timestamp = now()
    template_name = 'email/reporting_report.html'

    centre_report = compute_reporting(timestamp)

    # email the relevant portions
    with mail.get_connection() as mail_connection:
        for subscription in Subscription.objects.all():
            user = subscription.subscriber
            if not user.email:
                continue

            for location in subscription.locations.filter(
                            type__name__in=['Country', 'State']):
                report_data = centre_report.get(location.id)

                if report_data is None:
                    continue

                context = {
                    'month': calendar.month_name[timestamp.month],
                    'year': timestamp.year,
                    'report': report_data,
                    'location': location.name,
                    'location_type': location.type.name,
                }

                message = mail.EmailMessage(
                    subject='Birth Registration Reporting Summary',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                    body=render_to_string(template_name, context),
                    connection=mail_connection)
                message.content_subtype = 'html'
                message.send()


@shared_task
def prompt_nonreporting_reporters():
    reporting_date = now().replace(
        hour=0, minute=0, second=0, microsecond=0) - relativedelta(days=3)
    rc_ids = BirthRegistration.objects.filter(
        time=reporting_date).values_list('location__pk', flat=True)

    missing_rcs = Location.objects.filter(type__name='RC').exclude(
        pk__in=rc_ids)

    dataset = {}
    for rc in missing_rcs:
        # get the phone number from the last report sent
        # check the latest report for this
        report = rc.birthregistration_records.order_by('-time').first()
        if report:
            if report.connection and report.connection.identity:
                item = {
                    report.connection.identity: (
                        report.connection, report.reporter.full_name())
                }
                dataset.update(item)
        else:
            # or check the last BR reporter attached to this location
            reporter = rc.reporters.filter(role__code='BR').order_by(
                '-pk').first()
            if reporter:
                conn = reporter.connection()
                if conn and conn.identity:
                    item = {
                        conn.identity: (conn, reporter.full_name())
                    }
                    dataset.update(item)

    for connection, name in dataset.values():
        if connection is None:
            continue

        phone = connection.identity
        message = 'Dear {}, you have not yet sent your BR report for {:%d-%m-%Y}. Please send it now'.format(   # noqa
            name, reporting_date + relativedelta(hours=4))

        send_sms_message(message, phone)

        # log the outgoing message even though it's
        # not gone out via the RapidSMS infrastructure
        r_connection = Connection.objects.filter(
            identity=phone).order_by('-pk').first()
        Message.objects.create(
            connection=r_connection, direction='O', date=now(),
            text=message)


def compute_reports(year, month):
    ng = Location.get_by_code('ng')
    start_date = make_aware(datetime(year, month, 1))
    end_date = start_date + relativedelta(months=1, seconds=-1)

    report_params = [start_date, end_date, ng.id]
    prior_u1_params = [
        start_date + relativedelta(years=-4),
        start_date + relativedelta(seconds=-1),
        ng.id
    ]

    df = pd.read_sql_query(
        DATA_QUERY, db_connection, params=report_params).round()
    prior_u1_df = pd.read_sql_query(
        PRIOR_DATA_QUERY, db_connection, params=prior_u1_params)
    estimate_df = CensusResult.get_estimate_dataframe(year, month)

    # add in population estimates
    df[['estimate', 'u1_estimate', 'u5_estimate']] = df.apply(
        lambda row: estimate_df.loc[row['lga_id']], axis=1
    )

    # add in prior U1 reporting, required for U5 performance
    df['prior_u1'] = prior_u1_df['u1']

    # compute LGA performance
    df['u1_performance'] = df['u1'] / df['u1_estimate'] * 100
    df['u5_performance'] = (
        df['u5'] + df['prior_u1']) / df['u5_estimate'] * 100

    # rounding
    df = df.round({
        'estimate': 1,
        'u1_estimate': 1,
        'u1_performance': 1,
        'u5_estimate': 1,
        'u5_performance': 1,
    })

    report_data = {}
    grouped_df = df.groupby(['state_id', 'state'])
    national_breakdown = []

    # compute state stats
    for group_key in sorted(grouped_df.groups.keys(), key=itemgetter(1)):
        state_id, state_name = group_key
        state_stats = {'name': state_name}
        state_group = grouped_df.get_group(group_key).drop(
            ['state_id', 'state', 'lga_id'], axis=1
        ).rename(columns={'lga': 'name'})

        state_data = state_group.sum()
        state_data['name'] = state_name
        state_data['estimate'] = estimate_df.loc[state_id]['estimate']
        state_data['u1_estimate'] = estimate_df.loc[state_id]['u1_estimate']
        state_data['u5_estimate'] = estimate_df.loc[state_id]['u5_estimate']

        # compute performance
        state_data['u1_performance'] = round(
            state_data['u1'] / state_data['u1_estimate'] * 100, 1)
        state_data['u5_performance'] = round(
            (state_data['u5'] + state_data['prior_u1']) / state_data['u5_estimate'] * 100,
            1)

        # assemble
        state_stats['breakdown'] = state_group.fillna('-').to_dict(
            orient='records')
        state_stats['summary'] = state_data.fillna('-').to_dict()
        national_breakdown.append(state_stats['summary'])

        report_data[state_id] = state_stats

    # compute national stats
    national_data = df.sum().drop(['state_id', 'state', 'lga_id', 'lga'])
    national_data['name'] = ng.name
    national_data['estimate'] = estimate_df.loc[ng.id]['estimate']
    national_data['u1_estimate'] = estimate_df.loc[ng.id]['u1_estimate']
    national_data['u5_estimate'] = estimate_df.loc[ng.id]['u5_estimate']

    # compute performance
    national_data['u1_performance'] = round(national_data['u1'] / national_data['u1_estimate'] * 100, 1)
    national_data['u5_performance'] = round((
        national_data['u5'] + national_data['prior_u1']) / national_data['u5_estimate'] * 100, 1)

    report_data[ng.id] = {
        'breakdown': national_breakdown,
        'summary': national_data.fillna('-').to_dict()
    }

    return report_data


def compute_reporting(query_date):
    start_date = beginning_of_the_month(query_date)
    end_date = end_of_the_month(query_date)
    ng = Location.get_by_code('ng')

    params = [start_date, end_date, ng.id]
    reporting_df = pd.read_sql_query(
        CENTRE_REPORTING_QUERY, db_connection, params=params)

    report_data = {}
    national_breakdown = []
    grouped_df = reporting_df.groupby(['state_id', 'state'])

    for group_key in sorted(grouped_df.groups.keys(), key=itemgetter(1)):
        state_id, state_name = group_key
        state_stats = {'name': state_name}
        current_group = grouped_df.get_group(group_key).drop(
            ['state_id', 'state', 'lga_id'], axis=1
        ).rename(columns={'lga': 'name'})
        state_data = current_group.sum()
        state_data['name'] = state_name

        state_stats['breakdown'] = current_group.to_dict(orient='records')
        state_stats['summary'] = state_data
        national_breakdown.append(state_stats['summary'])

        report_data[state_id] = state_stats

    national_stats = {'name': ng.name}
    national_stats['breakdown'] = national_breakdown
    national_data = reporting_df.sum().drop(
        ['state', 'state_id', 'lga', 'lga_id'])
    national_data['name'] = ng.name
    national_stats['summary'] = national_data

    report_data[ng.id] = national_stats

    return report_data
