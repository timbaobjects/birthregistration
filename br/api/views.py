# -*- coding: utf-8 -*-
from datetime import date
import json
import os

from dateutil.relativedelta import relativedelta
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.db import connection
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
import pandas as pd

from django.conf import settings

from br import models, raw_queries, utils

CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


def _get_u1_reporting(boundary_dates, location_id):
    params = boundary_dates[0] + boundary_dates[0] + (location_id,)

    return pd.read_sql_query(
        raw_queries.U1_REPORTING_QUERY, connection, params=params)


def _get_u5_reporting(boundary_dates, location_id):
    params = boundary_dates[0] + boundary_dates[0] + (location_id,)

    return pd.read_sql_query(
        raw_queries.U5_REPORTING_QUERY, connection, params=params)


def _get_previous_u1_reporting(boundary_dates, location_id):
    previous_u1_reporting = [
        pd.read_sql_query(
            raw_queries.U1_PREVIOUS_PERIOD_QUERY, connection,
            params=(date_pair + (location_id,)))
        for date_pair in boundary_dates[1:]
    ]

    return previous_u1_reporting


def _get_previous_u5_reporting(boundary_dates, location_id):
    previous_u5_reporting = [
        pd.read_sql_query(
            raw_queries.U5_PREVIOUS_PERIOD_QUERY, connection,
            params=(date_pair + (location_id,)))
        for date_pair in boundary_dates[1:7]
    ]

    return previous_u5_reporting


def _get_previous_u1_reporting_for_u5(boundary_dates, location_id):
    previous_u5_reporting = [
        pd.read_sql_query(
            raw_queries.U5_PREVIOUS_U1_QUERY, connection,
            params=(date_pair + (location_id,)))
        for date_pair in boundary_dates[7:]
    ]

    return previous_u5_reporting


def _lga_transform(data_frame):
    return data_frame.drop(
        ['state', 'state_id'], axis=1
    ).rename(columns={'lga': 'location', 'lga_id': 'id'})


def _state_transform(data_frame):
    return data_frame.drop(
        ['lga', 'lga_id'], axis=1
    ).groupby(
        ['state', 'state_id']
    ).sum().reset_index().rename(columns={'state': 'location', 'state_id': 'id'})


def _transform_reporting(*reporting_dataframes):
    level = None
    current_reporting = reporting_dataframes[0]
    other_reporting = reporting_dataframes[1:]
    if current_reporting['state'].unique().size == 1:
        level = 'lga'
    else:
        level = 'state'

    if level == 'lga':
        operation = _lga_transform
    else:
        operation = _state_transform

    current_reporting = operation(current_reporting)
    other_reporting = [
        operation(df) for df in other_reporting
    ]

    return current_reporting, other_reporting, level


def _compute_u1_performance(date_pair, data_frame):
    difference = relativedelta(*date_pair)
    if difference.months == 0:
        # same month
        year = date_pair[0].year
        month = date_pair[0].month
    else:
        year = date_pair[0].year
        month = None

    estimate_dataframe = models.CensusResult.get_estimate_dataframe(
        year, month)

    estimates = estimate_dataframe.loc[data_frame['id']].reset_index()

    return (data_frame['u1'] / estimates['u1_estimate'] * 100).round(1)


def _compute_u5_performance(date_pair, data_frame, u1_data_frame):
    difference = relativedelta(*date_pair)
    if difference.months == 0:
        # same month
        year = date_pair[0].year
        month = date_pair[0].month
    else:
        year = date_pair[0].year
        month = None

    estimate_dataframe = models.CensusResult.get_estimate_dataframe(
        year, month)

    estimates = estimate_dataframe.loc[data_frame['id']].reset_index()

    return (
        (data_frame['u5'] + u1_data_frame['u1']) / estimates['u1_estimate'] * 100
    ).round(1)


def _get_geodata(level):
    filepath = os.path.join(settings.PROJECT_ROOT, 'base/static/base/js')
    filename = 'nga-{}s-mod.json'.format(level)

    with open(os.path.join(filepath, filename)) as f:
        geodata = json.load(f)

    geodata_map = {
        f['properties']['dbid']: json.dumps(f)
        for f in geodata['features']
    }

    return geodata_map


@cache_page(CACHE_TTL)
def get_u1_dashboard_data(request):
    dt = date.today()
    ng = models.Location.get_by_code('ng')

    ancestor_pk = request.GET.get('ancestor', ng.pk)
    try:
        year = int(request.GET.get('year', dt.year))
    except ValueError:
        return HttpResponseBadRequest()

    month = request.GET.get('month')
    try:
        if month is not None:
            month = int(month)
            if not (1 <= month <= 12):
                return HttpResponseBadRequest()
    except (TypeError, ValueError):
        return HttpResponseBadRequest()

    boundary_dates = utils.get_u1_boundary_dates(year, month)

    current_reporting = _get_u1_reporting(boundary_dates, ancestor_pk)
    if current_reporting.empty:
        return HttpResponseBadRequest()

    previous_reporting = _get_previous_u1_reporting(
        boundary_dates, ancestor_pk)

    current_reporting, previous_reporting, level = _transform_reporting(
        current_reporting, *previous_reporting)

    current_performance = _compute_u1_performance(
        boundary_dates[0], current_reporting)

    previous_performance = [
        _compute_u1_performance(date_pair, data_frame)
        for date_pair, data_frame in zip(
            boundary_dates[1:], previous_reporting)
    ]

    headers = ['location', 'current_performance']
    headers.extend([date_pair[0].year for date_pair in boundary_dates[1:4]])
    headers.extend([
        '{0:%m}-{0:%Y}'.format(date_pair[0])
        for date_pair in boundary_dates[4:]
    ])
    headers.extend([
        'boys', 'girls', 'centres', 'reporting_centres', 'new', 'geojson'])

    dataset = [
        current_reporting['location'].tolist(),
        current_performance.tolist()
    ]
    dataset.extend([
        perf.tolist() for perf in previous_performance
    ])
    dataset.extend([
        current_reporting['boys'].tolist(),
        current_reporting['girls'].tolist(),
        current_reporting['centre_count'].tolist(),
        current_reporting['reporting_centre_count'].tolist(),
        current_reporting['new_count'].tolist(),
    ])

    geodata_map = _get_geodata(level)
    geodata_column = [
        geodata_map.get(loc_id) for loc_id in current_reporting['id']
    ]
    dataset.append(geodata_column)

    output_dataframe = pd.DataFrame(zip(*dataset), columns=headers)
    response = HttpResponse(content_type='text/csv')
    output_dataframe.to_csv(response, encoding='UTF-8', index=False)

    return response


@cache_page(CACHE_TTL)
def get_u5_dashboard_data(request):
    dt = date.today()
    ng = models.Location.get_by_code('ng')

    ancestor_pk = request.GET.get('ancestor', ng.pk)
    try:
        year = int(request.GET.get('year', dt.year))
    except ValueError:
        return HttpResponseBadRequest()

    month = request.GET.get('month')
    try:
        if month is not None:
            month = int(month)
            if not (1 <= month <= 12):
                return HttpResponseBadRequest()
    except (TypeError, ValueError):
        return HttpResponseBadRequest()

    boundary_dates = utils.get_u5_boundary_dates(year, month)

    current_reporting = _get_u5_reporting(boundary_dates, ancestor_pk)
    if current_reporting.empty:
        return HttpResponseBadRequest()

    previous_u5_reporting = _get_previous_u5_reporting(
        boundary_dates, ancestor_pk)
    previous_u1_reporting = _get_previous_u1_reporting_for_u5(
        boundary_dates, ancestor_pk)
    previous_reporting = previous_u5_reporting + previous_u1_reporting

    current_reporting, previous_reporting, level = _transform_reporting(
        current_reporting, *previous_reporting)
    previous_u5_reporting = previous_reporting[:6]
    previous_u1_reporting = previous_reporting[6:]

    current_performance = _compute_u5_performance(
        boundary_dates[0], current_reporting, previous_u1_reporting[0])

    previous_performance = [
        _compute_u5_performance(date_pair, u5_data_frame, u1_data_frame)
        for date_pair, u5_data_frame, u1_data_frame in zip(
            boundary_dates[1:7], previous_u5_reporting,
            previous_u1_reporting[1:]
        )
    ]

    headers = ['location', 'current_performance']
    headers.extend([date_pair[0].year for date_pair in boundary_dates[1:4]])
    headers.extend([
        '{0:%m}-{0:%Y}'.format(date_pair[0])
        for date_pair in boundary_dates[4:7]
    ])
    headers.extend([
        'boys', 'girls', 'centres', 'reporting_centres', 'new', 'geojson'])

    dataset = [
        current_reporting['location'].tolist(),
        current_performance.tolist()
    ]
    dataset.extend([
        perf.tolist() for perf in previous_performance
    ])
    dataset.extend([
        current_reporting['boys'].tolist(),
        current_reporting['girls'].tolist(),
        current_reporting['centre_count'].tolist(),
        current_reporting['reporting_centre_count'].tolist(),
        current_reporting['new_count'].tolist(),
    ])

    geodata_map = _get_geodata(level)
    geodata_column = [
        geodata_map.get(loc_id) for loc_id in current_reporting['id']
    ]
    dataset.append(geodata_column)

    output_dataframe = pd.DataFrame(zip(*dataset), columns=headers)
    response = HttpResponse(content_type='text/csv')
    output_dataframe.to_csv(response, encoding='UTF-8', index=False)

    return response
