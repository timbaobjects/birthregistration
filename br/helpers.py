#!/usr/bin/env/python
# encoding=utf-8
from __future__ import unicode_literals
import functools
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import F, Func, SmallIntegerField, Sum
import pandas as pd
from .models import BirthRegistration


class ExtractMonth(Func):
    template = "EXTRACT(MONTH FROM %(expressions)s)"

    def __init__(self, *expressions, **extra):
        extra['output_field'] = SmallIntegerField()
        super(ExtractMonth, self).__init__(*expressions, **extra)



def memoize(obj):
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


def get_data_records(location, year, month=None):
    if month:
        start_date = datetime(year, month, 1) - relativedelta(years=1)
        end_date = datetime(year, month, 1) + relativedelta(months=1) - relativedelta(seconds=1)
    else:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 1, 1) + relativedelta(years=1) - relativedelta(seconds=1)

    descendant_nodes = location.nx_descendants()

    columns = [
        'boys_below1', 'boys_1to4', 'boys_5to9', 'boys_10to18',
        'girls_below1', 'girls_1to4', 'girls_5to9', 'girls_10to18',
    ]

    center_nodes = [
        node['id'] for node in descendant_nodes
        if node['type'] == 'RC' and node['active']]
    records = BirthRegistration.objects.filter(
        time__range=(start_date, end_date),
        location__pk__in=center_nodes
    )

    if location.type.name == u'Country':
        loc_ids = [node[u'id'] for node in descendant_nodes
            if node[u'type'] == u'State' and node[u'active']]

        records = records.annotate(month=ExtractMonth(u'time'),
            state_id=F(u'location__parent__parent__pk'),
            state_name=F(u'location__parent__parent__name'))

        value_cols = [u'state', u'state_id', u'month']
    elif location.type.name == u'State':
        loc_ids = [node[u'id'] for node in descendant_nodes
            if node[u'type'] == u'LGA' and node[u'active']]

        records = records.annotate(month=ExtractMonth(u'time'),
            lga=F(u'location__parent__name'), rc=F(u'location__name'),
            lga_id=F(u'location__parent__pk'), rc_id=F(u'location__pk'))

        value_cols = [u'lga', u'lga_id', u'rc', u'rc_id', u'month']
    else:
        raise ValueError(u'Please specify a country or a state')

    sum_kwargs = {u'sum_{}'.format(c): Sum(c) for c in columns}

    records = records.values(*value_cols).annotate(**sum_kwargs)

    return records


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

