#!/usr/bin/env/python
# encoding=utf-8
from __future__ import unicode_literals
import functools
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
from .models import BirthRegistration


def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


def get_record_dataset(location, year, month=None, cumulative=False):
    if month:
        start_date = datetime(year, month, 1) - relativedelta(years=1)
        end_date = datetime(year, month, 1) + relativedelta(months=1) - relativedelta(seconds=1)
    else:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 1, 1) + relativedelta(years=1) - relativedelta(seconds=1)

    if cumulative:
        start_date = datetime.fromtimestamp(0)

    center_nodes = [
        node['id'] for node in location.nx_descendants()
        if node['type'] == 'RC' and node['active']]
    records = BirthRegistration.objects.filter(
        time__range=(start_date, end_date),
        location__pk__in=center_nodes
    )

    if not records.exists():
        index = pd.date_range(start_date, end_date)
        columns = [
            'boys_below1', 'boys_1to4', 'boys_5to9', 'boys_10to18',
            'girls_below1', 'girls_1to4', 'girls_5to9', 'girls_10to18',
            'below1', '1to4', '5to9', '10to18', 'above5', 'boys_above5',
            'girls_above5', 'rc', 'lga', 'state'
        ]
        return pd.DataFrame(index=index, columns=columns).fillna(0)

    dataset = pd.DataFrame(
        list(records.values(
            'time', 'girls_below1', 'girls_1to4', 'girls_5to9', 'girls_10to18',
            'boys_below1', 'boys_1to4', 'boys_5to9', 'boys_5to9',
            'boys_10to18', 'location__name', 'location__parent__name',
            'location__parent__parent__name',
        ))
    ).rename(columns={'location__name':'rc',
        'location__parent__name': 'lga',
        'location__parent__parent__name': 'state'})

    dataset['below1'] = dataset['boys_below1'] + dataset['girls_below1']
    dataset['1to4'] = dataset['boys_1to4'] + dataset['girls_1to4']
    dataset['5to9'] = dataset['boys_5to9'] + dataset['girls_5to9']
    dataset['10to18'] = dataset['boys_10to18'] + dataset['girls_10to18']
    dataset['above5'] = dataset['5to9'] + dataset['10to18']
    dataset['boys_above5'] = dataset['boys_5to9'] + dataset['boys_10to18']
    dataset['girls_above5'] = dataset['girls_5to9'] + dataset['girls_10to18']
    dataset['total'] = dataset['below1'] + dataset['1to4'] + dataset['above5']

    return dataset.set_index('time').sort_index()


def stringify(s):
    if s is None:
        return ''

    return unicode(s)

