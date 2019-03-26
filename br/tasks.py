from __future__ import absolute_import
from br.helpers import get_performance_dataframe, get_nonperforming_locations
from br.models import BirthRegistration, Subscription
from reporters.models import Reporter
from messaging.utils import send_sms_message
from celery import shared_task
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.timezone import now
import pandas as pd


def beginning_of_the_month(dt):
    return datetime(dt.year, dt.month, 1)


def end_of_the_month(dt):
    if dt.month == 12: # if the month is December, then return Jan. 1 of the next year
        return datetime(dt.year + 1, 1, 1)
    else: # if not, subtract one second from the next month
        return datetime(dt.year, dt.month + 1, 1) - relativedelta(seconds=1)


def compute_performance(subscription):
    # extract the best performing and worst performing locations
    # TODO: add protections for a mixture of location types in the subscription
    summary = pd.DataFrame()
    report_region = None
    best_performing_under1 = []
    best_performing_under5 = []
    worst_performing_under1 = []
    worst_performing_under5 = []
    locations = subscription.locations.filter(type__name__in=['Country', 'State'])
    for location in locations:
        if location.type.name == "Country":
            report_region = "State"
        elif location.type.name == "State":
            report_region = "LGA"

        dataframe, _ = get_performance_dataframe(location, datetime.now().year, datetime.now().month)
        dataframe = dataframe.fillna(0)
        summary = summary.append(dataframe)

    # now sort the summary dataframe to get the two best and worst performing
    if not summary.empty:
        best_performing_under1 = [{
            'name': report[1][report_region.lower()],
            'performance': report[1]['U1 Performance'] * 100}
            for report in summary.sort_values('U1 Performance', ascending=False).head(2).iterrows()]
        best_performing_under5 = [{
            'name': report[1][report_region.lower()],
            'performance': report[1]['U5 Performance'] * 100}
            for report in summary.sort_values('U5 Performance', ascending=False).head(2).iterrows()]
        worst_performing_under1 = [{
            'name': report[1][report_region.lower()],
            'performance': report[1]['U1 Performance'] * 100}
            for report in summary.sort_values('U1 Performance', ascending=True).head(2).iterrows()]
        worst_performing_under5 = [{
            'name': report[1][report_region.lower()],
            'performance': report[1]['U5 Performance'] * 100}
            for report in summary.sort_values('U5 Performance', ascending=True).head(2).iterrows()]

    context = {
        'best_under1': best_performing_under1,
        'best_under5': best_performing_under5,
        'worst_under1': worst_performing_under1,
        'worst_under5': worst_performing_under5,
        'report_region': report_region,
        'today': datetime.now(),
    }
    return context


def compute_nonreporting(subscription, end_of_month=False):
    report_region = None
    today = datetime.now()
    start_date = beginning_of_the_month(today)
    end_date = end_of_the_month(today) if end_of_month else today
    nonreporting_locations = []
    for location in subscription.locations.filter(type__name__in=['Country', 'State']):
        if location.type.name == "Country":
            report_region = "State"
        elif location.type.name == "State":
            report_region = "LGA"
        for loc in get_nonperforming_locations(location, start_date, end_date):
            nonreporting_locations.append(
                {'name': loc, 'type': report_region})

    return {
        'report_region': report_region,
        'non_reporting': nonreporting_locations, 'today': datetime.now()}

@shared_task
def mid_month_reports():
    for subscription in Subscription.objects.filter(is_active=True):
        mid_month_report.delay(subscription.pk)

@shared_task
def mid_month_report(subscription_id):
    # TODO: text-formatted version of the email
    subscription = Subscription.objects.get(pk=subscription_id)
    context = compute_nonreporting(subscription, False)
    email_subject = 'Birth Registration Mid-Month Summary'
    email_body = render_to_string('email/mid-month-report.html', context)
    user = subscription.subscriber
    if user.email:
        send_mail(
            email_subject, u'', settings.DEFAULT_FROM_EMAIL, [user.email],
            html_message=email_body)


@shared_task
def monthly_reports():
    for subscription in Subscription.objects.filter(is_active=True):
        month_report.delay(subscription.pk)


@shared_task
def month_report(subscription_id):
    # TODO: text-formatted version of the email
    subscription = Subscription.objects.get(pk=subscription_id)
    context = compute_performance(subscription)
    context.update(compute_nonreporting(subscription, True))
    email_subject = 'Birth Registration Monthly Summary'
    email_body = render_to_string('email/end-month-report.html', context)
    user = subscription.subscriber
    if user.email:
        send_mail(
            email_subject, u'', settings.DEFAULT_FROM_EMAIL, [user.email],
            html_message=email_body)


@shared_task
def prompt_nonreporting_reporters():
    reporting_date = now().replace(
        hour=0, minute=0, second=0, microsecond=0) - relativedelta(days=3)
    rc_ids = BirthRegistration.objects.filter(
        time=reporting_date).values_list('location__pk', flat=True)

    reporters = Reporter.objects.filter(
        role__code='BR', location__active=True, location__type__name='RC'
    ).exclude(
        location__pk__in=rc_ids
    )

    dataset = {(r.connection(), r.full_name()) for r in reporters}
    for connection, name in dataset:
        if connection is None:
            continue

        phone = connection.identity
        message = 'Dear {}, you have not yet sent your BR report for {:%d-%m-%Y}. Please send it now'.format(   # noqa
            name, reporting_date + relativedelta(hours=4))

        send_sms_message(message, phone)
