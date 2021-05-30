# -*- coding: utf-8 -*-
import json
import os

import pandas as pd
from django.db import connection
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from br.api import queries
from br.models import CensusResult
from br.utils import get_boundary_dates
from locations.models import Location

data_file_path = os.path.join(os.path.dirname(__file__), 'data/estimates.csv')

if os.path.exists(data_file_path):
    ESTIMATE_DATAFRAME = pd.read_csv(data_file_path).set_index('loc_id').sort_index()
else:
    ESTIMATE_DATAFRAME = pd.DataFrame(
        {},
        columns=['estimate', 'u1_estimate', 'u5_estimate', 'year', 'month',
                 'loc_id']
    ).set_index('loc_id')


def get_estimate_dataframe(year, month=None):
    ss_year = ESTIMATE_DATAFRAME[ESTIMATE_DATAFRAME['year'] == year]

    if month is None:
        subset = ss_year[ss_year['month'] == 12]
    else:
        subset = ss_year[ss_year['month'] == month]

    if subset.empty:
        return CensusResult.get_estimate_dataframe(year, month)

    return subset[['estimate', 'u1_estimate', 'u5_estimate']]


def get_dataframe(level, year, month):
    start, end, u1_start, u1_end = get_boundary_dates(year, month)

    reporting_params = [start, end, start, end]
    prior_u1_params = [u1_start, u1_end]

    reporting_attribute_name = level.upper() + '_REPORTING_QUERY'
    prior_attribute_name = level.upper() + '_PREV_U1_QUERY'
    
    query_reporting = getattr(queries, reporting_attribute_name, None)
    query_prior = getattr(queries, prior_attribute_name, None)

    if query_reporting is None or query_prior is None:
        return pd.DataFrame()

    reporting_dataframe = pd.read_sql_query(
        query_reporting, connection, params=reporting_params).fillna(0)
    prior_u1_dataframe = pd.read_sql_query(
        query_prior, connection, params=prior_u1_params).fillna(0)
    # estimate_df = CensusResult.get_estimate_dataframe(year, month)
    estimate_df = get_estimate_dataframe(year, month)

    if level == 'country':
        loc = Location.get_by_code('ng')
        reporting_dataframe['loc_id'] = loc.id
        reporting_dataframe['loc'] = loc.name
        prior_u1_dataframe['loc_id'] = loc.id
        prior_u1_dataframe['loc'] = loc.name

    dataframe = pd.concat([
        reporting_dataframe.set_index('loc_id'),
        prior_u1_dataframe.drop('loc', axis=1).set_index('loc_id'),
        estimate_df
    ], axis=1, join='inner')

    dataframe['u1_perf'] = dataframe['u1'] / dataframe['u1_estimate']
    dataframe['u5_perf'] = (dataframe['u5'] + dataframe['prev_u1']) / dataframe['u5_estimate']

    return dataframe


def get_dataframe_lite(level, year, month):
    start, end, u1_start, u1_end = get_boundary_dates(year, month)

    reporting_params = [start, end]
    prior_u1_params = [u1_start, u1_end]

    reporting_attribute_name = level.upper() + '_REPORTING_LITE_QUERY'
    prior_attribute_name = level.upper() + '_PREV_U1_QUERY'
    
    query_reporting = getattr(queries, reporting_attribute_name, None)
    query_prior = getattr(queries, prior_attribute_name, None)

    if query_reporting is None or query_prior is None:
        return pd.DataFrame()

    reporting_dataframe = pd.read_sql_query(
        query_reporting, connection, params=reporting_params).fillna(0)
    prior_u1_dataframe = pd.read_sql_query(
        query_prior, connection, params=prior_u1_params).fillna(0)
    # estimate_df = CensusResult.get_estimate_dataframe(year, month)
    estimate_df = get_estimate_dataframe(year, month)

    if level == 'country':
        loc = Location.get_by_code('ng')
        reporting_dataframe['loc_id'] = loc.id
        reporting_dataframe['loc'] = loc.name
        prior_u1_dataframe['loc_id'] = loc.id
        prior_u1_dataframe['loc'] = loc.name

    dataframe = pd.concat([
        reporting_dataframe.set_index('loc_id'),
        prior_u1_dataframe.drop('loc', axis=1).set_index('loc_id'),
        estimate_df
    ], axis=1, join='inner')

    dataframe['u1_perf'] = dataframe['u1'] / dataframe['u1_estimate']
    dataframe['u5_perf'] = (dataframe['u5'] + dataframe['prev_u1']) / dataframe['u5_estimate']

    return dataframe


def get_api_data(level='country', year=None, month=None):
    level = level.lower()
    if year is None:
        year = now().year

    if level not in ('country', 'state', 'lga'):
        return {}

    dataframe_primary = get_dataframe(level, year, month)
    years = list(range(year - 3, year))
    alt_dataframes = [get_dataframe_lite(level, yr, None) for yr in years]

    map_data_folder = os.path.join(os.path.dirname(__file__), 'json')
    geodata_filename = 'br-api-{level}.json'.format(level=level)
    map_data = os.path.join(map_data_folder, geodata_filename)

    if not os.path.exists(map_data):
        return {}

    with open(map_data) as f:
        payload = json.load(f)

    if not dataframe_primary.empty:
        for feature in payload['features']:
            loc_id = feature.get('properties').get('id')
            data = {}
            record = dataframe_primary.loc[loc_id]
            data.update(
                u1=record['u1'],
                u5=record['u5'],
                five_plus=record['five_plus'],
                u1_boys=record['u1_boys'],
                u5_boys=record['u5_boys'],
                five_plus_boys=record['five_plus_boys'],
                u1_girls=record['u1_girls'],
                u5_girls=record['u5_girls'],
                five_plus_girls=record['five_plus_girls'],
                boys=record['boys'],
                girls=record['girls'],
                u1_perf=round(record['u1_perf'] * 100, 2),
                u5_perf=round(record['u5_perf'] * 100, 2),
                u1_estimate=round(record['u1_estimate']),
                u5_estimate=round(record['u5_estimate']),
                estimate=round(record['estimate']),
                total_centres=record['total_centres'],
                reporting_centres=record['reporting_centres'],
                new_centres=record['new_centres'],
                year=year,
                month=month
            )

            previous = []
            for year, alt_df in zip(years, alt_dataframes):
                try:
                    subset = alt_df.loc[loc_id]

                    previous.append({
                        'year': year,
                        'u1_perf': round(subset['u1_perf'] * 100, 2),
                        'u5_perf': round(subset['u5_perf'] * 100, 2),
                        'u1_estimate': round(subset['u1_estimate'] * 100, 2),
                        'u5_estimate': round(subset['u5_estimate'] * 100, 2),
                    })
                except KeyError:
                    previous.append({
                        'year': year,
                        'u1_perf': 0,
                        'u5_perf': 0,
                        'u1_estimate': 0,
                        'u5_estimate': 0,
                    })

            data.update(previous=previous)
            feature['properties'].update(data)

    return payload
