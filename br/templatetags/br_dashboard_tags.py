import calendar
from datetime import datetime

from django import template
from django.conf import settings
from pandas import isnull

from br.helpers import memoize, get_u1_reporting_for_past_4_years
from br.models import CensusResult
from locations.models import Location


register = template.Library()


@register.filter
def br_default(value):
    if isnull(value) or value == '':
        return '-'

    try:
        return int(value)
    except TypeError, ValueError:
        return '-'


@register.simple_tag
def performance_pct(value):
    if value is None or isinstance(value, str):
        return '0'
    return '{:.0f}'.format(value)


@register.simple_tag
def performance_class(value):
    if value is None or isinstance(value, str):
        return 'label-danger'
    p = value / 100
    if p >= 0.7:
        return 'label-success'
    elif 0.3 <= p < 0.7:
        return 'label-warning'
    else:
        return 'label-danger'


@register.simple_tag
def month_name(month_index):
    return calendar.month_name[month_index]
