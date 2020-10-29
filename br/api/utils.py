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


def get_dataframe(level, year, month):
    start, end, u1_start, u1_end = get_boundary_dates(year, month)

    reporting_params = [start, end, start, end]
    prior_u1_params = [u1_start, u1_end]

    if level == 'country':
        query_reporting = queries.NATIONAL_REPORTING_QUERY
        query_prior = queries.NATIONAL_PREV_U1_QUERY
    else:
        query_reporting = queries.STATE_REPORTING_QUERY
        query_prior = queries.STATE_PREV_U1_QUERY

    reporting_dataframe = pd.read_sql_query(
        query_reporting, connection, params=reporting_params).fillna(0)
    prior_u1_dataframe = pd.read_sql_query(
        query_prior, connection, params=prior_u1_params).fillna(0)
    estimate_df = CensusResult.get_estimate_dataframe(year, month)

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

    if level == 'country':
        query_reporting = queries.NATIONAL_REPORTING_LITE_QUERY
        query_prior = queries.NATIONAL_PREV_U1_QUERY
    else:
        query_reporting = queries.STATE_REPORTING_LITE_QUERY
        query_prior = queries.STATE_PREV_U1_QUERY

    reporting_dataframe = pd.read_sql_query(
        query_reporting, connection, params=reporting_params).fillna(0)
    prior_u1_dataframe = pd.read_sql_query(
        query_prior, connection, params=prior_u1_params).fillna(0)
    estimate_df = CensusResult.get_estimate_dataframe(year, month)

    dataframe = pd.concat([
        reporting_dataframe.set_index('loc_id'),
        prior_u1_dataframe.drop('loc', axis=1).set_index('loc_id'),
        estimate_df
    ], axis=1, join='inner')

    dataframe['u1_perf'] = dataframe['u1'] / dataframe['u1_estimate']
    dataframe['u5_perf'] = (dataframe['u5'] + dataframe['prev_u1']) / dataframe['u5_estimate']

    return dataframe


def get_api_data(level='country', year=None, month=None):
    if year is None:
        year = now().year

    dataframe_primary = get_dataframe(level, year, month)
    years = list(range(year - 3, year))
    alt_dataframes = [get_dataframe_lite(level, yr, None) for yr in years]

    map_data_folder = os.path.join(os.path.dirname(__file__), 'json')
    if level == 'country':
        map_data = os.path.join(map_data_folder, 'br-api-states.json')
        with open(map_data) as f:
            geojson = json.load(f)
    else:
        map_data = os.path.join(map_data_folder, 'br-api-lgas.json')
        with open(map_data) as f:
            geojson = json.load(f)

    if not dataframe_primary.empty:
        for feature in geojson['features']:
            loc_id = feature.get('properties').get('id')
            data = {}
            record = dataframe_primary.loc[loc_id]
            data.update(
                u1=record['u1'],
                u5=record['u5'],
                boys=record['boys'],
                girls=record['girls'],
                u1_perf=round(record['u1_perf'] * 100, 2),
                u5_perf=round(record['u5_perf'] * 100, 2),
                u1_estimate=round(record['u1_estimate']),
                u5_estimate=round(record['u5_estimate']),
                total_centres=record['total_centres'],
                reporting_centres=record['reporting_centres'],
                new_centres=record['new_centres'],
                year=year,
                month=month
            )
            data.update(previous=[{
                'year': year,
                'u1_perf': round(alt_df.loc[loc_id]['u1_perf'] * 100, 2),
                'u5_perf': round(alt_df.loc[loc_id]['u5_perf'] * 100, 2),
                'u1_estimate': round(alt_df.loc[loc_id]['u1_estimate']),
                'u5_estimate': round(alt_df.loc[loc_id]['u5_estimate']),
            } for year, alt_df in zip(years, alt_dataframes)])
            feature['properties'].update(data)

    return geojson
