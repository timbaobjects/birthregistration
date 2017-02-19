#!/usr/bin/env/python
# encoding=utf-8
from __future__ import unicode_literals
import functools
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import F, Func, SmallIntegerField, Sum
import pandas as pd
from locations.models import Location
from .models import BirthRegistration, CensusResult


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


def get_population_estimate(row, year, month=None):
    if month:
        growth_rate = ((1 + row[u'growth_rate']) ** (1 / 12.0)) - 1
        exponent = (year - row[u'year'] - 1) + month
    else:
        growth_rate = row[u'growth_rate']
        exponent = year - row[u'year']
    estimate = row[u'population'] * ((1 + (growth_rate / 100.0)) ** exponent)
    return estimate


def get_population_growth(year, month=None):
    # if there's no month, we're computing the difference between the
    # previous year and the passed-in year
    if month is None:
        df_year = CensusResult.get_census_dataframe(year)
        df_year_prev = CensusResult.get_census_dataframe(year - 1)

        pop_estimator = functools.partial(get_population_estimate, year=year)

        current_estimate = df_year.apply(pop_estimator, axis=1)
        prev_estimate = df_year_prev.apply(pop_estimator, axis=1)

    # at the beginning of the year, we're computing between the end of the
    # previous year, and the current one
    elif month == 1:
        df_year = CensusResult.get_census_dataframe(year)
        df_year_prev = CensusResult.get_census_dataframe(year - 1)

        pop_estimator = functools.partial(get_population_estimate, year=year, month=month)
        pop_estimator_prev = functools.partial(get_population_estimate, year=year - 1, month=12)

        current_estimate = df_year.apply(pop_estimator, axis=1)
        prev_estimate = df_year_prev.apply(pop_estimator_prev, axis=1)

    # otherwise, we're just calculating the difference between successive months,
    # the larger of which is specified
    else:
        df_year = CensusResult.get_census_dataframe(year)
        pop_estimator = functools.partial(get_population_estimate, year=year, month=month)
        pop_estimator_prev = functools.partial(get_population_estimate, year=year, month=month - 1)

        current_estimate = df_year.apply(pop_estimator, axis=1)
        prev_estimate = df_year.apply(pop_estimator_prev, axis=1)

    return current_estimate - prev_estimate


def get_data_records(location, year, month=None):
    if month:
        start_date = datetime(year, month, 1)
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
        subnodes = [node for node in descendant_nodes
            if node[u'type'] == u'State' and node[u'active']]

        records = records.annotate(
            state_id=F(u'location__parent__parent__pk'),
            state=F(u'location__parent__parent__name'))

        value_cols = [u'state', u'state_id']
    elif location.type.name == u'State':
        subnodes = [node for node in descendant_nodes
            if node[u'type'] == u'LGA' and node[u'active']]

        records = records.annotate(lga=F(u'location__parent__name'),
            lga_id=F(u'location__parent__pk'))

        value_cols = [u'lga', u'lga_id']
    else:
        raise ValueError(u'Please specify a country or a state')

    sum_kwargs = {u'sum_{}'.format(c): Sum(c) for c in columns}

    records = records.values(*value_cols).annotate(**sum_kwargs)
    df_columns = sum_kwargs.keys() + value_cols

    if not records.exists():
        if location.type.name == u'Country':
            col1 = u'state_id'
            col2 = u'state'
        elif location.type.name == u'State':
            col1 = u'lga_id'
            col2 = u'lga'

        dummy_records = []
        for node in subnodes:
            record = {c: None for c in df_columns}
            record.update({col1: node[u'id'], col2: node[u'name']})

            dummy_records.append(record)

        dataframe = pd.DataFrame.from_records(dummy_records, columns=df_columns)
    else:
        dataframe = pd.DataFrame.from_records(records, columns=df_columns)

    dataframe[u'under_1'] = dataframe[u'sum_boys_below1'] + dataframe[u'sum_girls_below1']
    dataframe[u'1to4'] = dataframe[u'sum_boys_1to4'] + dataframe[u'sum_girls_1to4']
    dataframe[u'above5'] = dataframe[u'sum_boys_5to9'] + dataframe[u'sum_girls_5to9'] + \
        dataframe[u'sum_boys_10to18'] + dataframe[u'sum_girls_10to18']

    return dataframe, subnodes


def get_performance_dataframe(location, year, month=None):
    if location.type.name == u'Country':
        index_col = u'state_id'
    elif location.type.name == u'State':
        index_col = u'lga_id'
    dataframe, subnodes = get_data_records(location, year, month)
    dataframe = dataframe.set_index(index_col)
    dataframe[u'U1 Performance'] = None
    dataframe[u'U5 Performance'] = None

    census_data = CensusResult.get_census_dataframe(year)
    # census_data[u'growth'] = get_population_growth(year, month)
    census_data[u'estimate'] = census_data.apply(
        functools.partial(get_population_estimate, year=year, month=month),
        axis=1)

    for node in subnodes:
        row = dataframe.loc[node[u'id']]
        u1_numerator = row[u'under_1']
        u5_numerator = row[[u'under_1', u'1to4']].sum()
        node_census_data = census_data.loc[node[u'id']]
        # u1_denominator = node_census_data[u'growth'] * node_census_data[u'under_1_rate'] * 0.01
        u1_denominator = node_census_data[u'estimate'] * node_census_data[u'under_1_rate'] * 0.01
        # u5_denominator = node_census_data[u'growth'] * node_census_data[u'under_5_rate'] * 0.01
        u5_denominator = node_census_data[u'estimate'] * node_census_data[u'under_5_rate'] * 0.01

        dataframe.loc[node[u'id'], u'U1 Performance'] = (u1_numerator / u1_denominator) * 100
        dataframe.loc[node[u'id'], u'U5 Performance'] = (u5_numerator / u5_denominator) * 100

    return dataframe, subnodes


def get_nonperforming_locations(location, start_date, end_date):
    descendant_nodes = location.nx_descendants()
    rc_pks = [n[u'id'] for n in descendant_nodes if n[u'type'] == u'RC']
    rcs = Location.objects.filter(type__name=u'RC', pk__in=rc_pks)

    reports = BirthRegistration.objects.filter(
        time__range=(start_date, end_date),
        location__pk__in=rc_pks)
    reported_pks = reports.values_list(u'location__pk', flat=True)

    qs = rcs.exclude(pk__in=reported_pks)

    if location.type.name == u'Country':
        return set(qs.values_list(u'parent__parent__name', flat=True))
    elif location.type.name == u'State':
        return set(qs.values_list(u'parent__name', flat=True))
    else:
        return set(qs.values_list(u'name', flat=True))


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
