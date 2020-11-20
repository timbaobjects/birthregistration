# -*- coding: utf-8 -*-
import calendar
import csv
from datetime import datetime
from io import BytesIO
from operator import itemgetter

from dateutil.relativedelta import relativedelta
from django.db import connection
from django.utils.timezone import make_aware, now
import pandas as pd

from br import raw_queries


def get_report_year_range():
    cursor = connection.cursor()
    cursor.execute('SELECT MIN(time), MAX(time) FROM br_birthregistration')
    result = cursor.fetchone()

    if result is None:
        current_timestamp = now()
        return (current_timestamp.year, current_timestamp.year)
    
    return [d.year for d in result]


def compute_estimate(census_results, year, month, record):
    '''
    Computes estimates for a record of aggregated birth registration data.

    Arguments:
        census_results - a pandas DataFrame of saved census data
        year - the year the estimates are computed for
        month - the month for which estimates are computed
                pass None for this if annual estimates are required
        record - a single row of aggregated BR data, as a pandas
                 Series.

    Returns:
        the location database ID, the population estimate, the U1
        estimate and the U5 estimate as a tuple. If the location
        has no saved census data, the last three will be None

    This function is meant to be converted into a partial and called
    using the pandas DataFrame method apply().
    '''
    try:
        subset = census_results.loc[record.name]
    except KeyError:
        # the location has no saved census data
        return record.name, None, None, None

    # adjust for month or year estimate
    if month is None:
        growth_rate = subset['growth_rate']
        exponent = year - subset['year']
    else:
        growth_rate = growth_rate = ((1 + subset[u'growth_rate']) ** (1 / 12.0)) - 1
        exponent = (year - subset[u'year'] - 1) + month

    estimate = subset['population'] * ((1 + (growth_rate / 100.0)) ** exponent)
    u1_estimate = subset['under_1_rate'] * 0.01 * estimate
    u5_estimate = subset['under_5_rate'] * 0.01 * estimate

    return record.name, estimate, u1_estimate, u5_estimate


def compute_performance(prior_u1_df, record):
    '''
    Computes performance for an aggregated BR record

    Arguments:
        prior_u1_df - a pandas DataFrame with aggregated U1 data
        record - a single row of aggregated BR data with estimate
                 data, as a pandas Series

    Returns:
        the location database ID, the U1 performance and the U5
        performance as a tuple. If there is no prior U1 data,
        the last two will be None
    '''
    if prior_u1_df.empty:
        subset = {'u1': 0}
    else:
        try:
            subset = prior_u1_df.loc[record.name]
        except KeyError:
            return record.name, None, None, None

    u1_performance = round(record['u1'] / record['u1_estimate'] * 100.0, 2)
    u5_performance = round(
        (record['u5'] + subset['u1']) / record['u5_estimate'] * 100.0, 2)

    return record.name, u1_performance, u5_performance, subset['u1']


def get_boundary_dates(year, month):
    if month:
        start_date = make_aware(datetime(year, month, 1))
        end_date = start_date + relativedelta(months=1, seconds=-1)
    else:
        start_date = make_aware(datetime(year, 1, 1))
        end_date = start_date + relativedelta(years=1, seconds=-1)

    u1_lower_bound = start_date - relativedelta(years=4)
    u1_upper_bound = u1_lower_bound + relativedelta(years=4, seconds=-1)

    return start_date, end_date, u1_lower_bound, u1_upper_bound


def extract_reporting_records(location, year, month):
    level = location.type.name.lower()
    start_date, end_date, u1_lower_bound, u1_upper_bound = get_boundary_dates(
        year, month)
    params_reporting = []
    params_prior_reporting = []

    if level == 'country':
        query_reporting = raw_queries.NATIONAL_REPORTING_QUERY
        query_u1_prior = raw_queries.NATIONAL_PRIOR_U1_REPORTING_QUERY
        params_reporting = [start_date, end_date]
        params_prior_reporting = [u1_lower_bound, u1_upper_bound]
    else:
        query_reporting = raw_queries.STATE_REPORTING_QUERY
        query_u1_prior = raw_queries.STATE_PRIOR_U1_REPORTING_QUERY
        params_reporting = [start_date, end_date, location.id]
        params_prior_reporting = [u1_lower_bound, u1_upper_bound, location.id]

    reporting_df = pd.read_sql_query(
        query_reporting, connection, params=params_reporting)
    prior_u1_df = pd.read_sql_query(
        query_u1_prior, connection, params=params_prior_reporting)

    reporting_df['u1'] = reporting_df['girls_below1'] + \
        reporting_df['boys_below1']
    reporting_df['u5'] = reporting_df['u1'] + \
        reporting_df['girls_1to4'] + reporting_df['boys_1to4']
    reporting_df['u5_girls'] = reporting_df['girls_below1'] + \
        reporting_df['girls_1to4']
    reporting_df['u5_boys'] = reporting_df['boys_below1'] + \
        reporting_df['boys_1to4']
    reporting_df['one_to_four'] = reporting_df['girls_1to4'] + \
        reporting_df['boys_1to4']
    reporting_df['girls_five_plus'] = reporting_df['girls_5to9'] + \
        reporting_df['girls_10to18']
    reporting_df['boys_five_plus'] = reporting_df['boys_5to9'] + \
        reporting_df['boys_10to18']
    reporting_df['five_plus'] = reporting_df['girls_five_plus'] + \
        reporting_df['boys_five_plus']
    reporting_df['girls'] = reporting_df['u5_girls'] + \
        reporting_df['girls_five_plus']
    reporting_df['boys'] = reporting_df['u5_boys'] + \
        reporting_df['boys_five_plus']
    reporting_df['total'] = reporting_df['girls'] + reporting_df['boys']

    return reporting_df, prior_u1_df


def extract_cumulative_records(location, year, month):
    if month is None:
        month = 12
        day = 31
    else:
        day = calendar.monthrange(year, month)[1]
    start_date = make_aware(datetime(year, month, day, 23, 59, 59, 999))
    params_reporting = []

    if location.type.name.lower() == 'country':
        query_reporting = raw_queries.NATIONAL_CUMULATIVE_QUERY
        params_reporting = [start_date]
    else:
        query_reporting = raw_queries.STATE_CUMULATIVE_QUERY
        params_reporting = [location.id, start_date]

    reporting_df = pd.read_sql_query(
        query_reporting, connection, params=params_reporting)

    reporting_df['u1'] = reporting_df['girls_below1'] + \
        reporting_df['boys_below1']
    reporting_df['u5'] = reporting_df['u1'] + \
        reporting_df['girls_1to4'] + reporting_df['boys_1to4']
    reporting_df['u5_girls'] = reporting_df['girls_below1'] + \
        reporting_df['girls_1to4']
    reporting_df['u5_boys'] = reporting_df['boys_below1'] + \
        reporting_df['boys_1to4']
    reporting_df['one_to_four'] = reporting_df['girls_1to4'] + \
        reporting_df['boys_1to4']
    reporting_df['girls_five_plus'] = reporting_df['girls_5to9'] + \
        reporting_df['girls_10to18']
    reporting_df['boys_five_plus'] = reporting_df['boys_5to9'] + \
        reporting_df['boys_10to18']
    reporting_df['five_plus'] = reporting_df['girls_five_plus'] + \
        reporting_df['boys_five_plus']
    reporting_df['girls'] = reporting_df['u5_girls'] + \
        reporting_df['girls_five_plus']
    reporting_df['boys'] = reporting_df['u5_boys'] + \
        reporting_df['boys_five_plus']
    reporting_df['total'] = reporting_df['girls'] + reporting_df['boys']

    return reporting_df


def export_dataset(data_frame, writer):
    old_columns = [
        'state',
        'lga',
        'girls_below1',
        'girls_1to4',
        'girls_5to9',
        'girls_10to18',
        'boys_below1',
        'boys_1to4',
        'boys_5to9',
        'boys_10to18',
        'u1',
        'u5',
        'one_to_four',
        'five_plus',
        'estimate',
        'u1_estimate',
        'u5_estimate',
        'u1_performance',
        'u5_performance',
    ]

    new_columns = [
        'State',
        'LGA',
        'Girls < 1',
        'Girls 1 to 4',
        'Girls 5 to 9',
        'Girls 10+',
        'Boys < 1',
        'Boys 1 to 4',
        'Boys 5 to 9',
        'Boys 10+',
        'U1',
        'U5',
        'Total 1 to 4',
        'Total 5+',
        'Estimate',
        'U1 estimate',
        'U5 estimate',
        'U1 performance',
        'U5 performance',
    ]

    column_map = {
        old_col: new_col for old_col, new_col in zip(old_columns, new_columns)}

    data_frame2 = data_frame.rename(columns=column_map)
    exportable_columns = [
        c for c in new_columns
        if c in data_frame2.columns
    ]

    data_frame2[exportable_columns].to_excel(writer, index=False)
    writer.save()


def get_reporting_range():
    cursor = connection.cursor()
    cursor.execute(raw_queries.REPORTING_RANGE_QUERY)

    return cursor.fetchone()


def get_national_subnodes():
    cursor = connection.cursor()
    cursor.execute(raw_queries.STATE_NODES_QUERY)

    state_nodes = []
    for record in cursor.fetchall():
        state_nodes.append({
            k: v for k, v in zip(['id', 'name', 'type'], record)
        })

    return state_nodes


def get_state_subnodes(state):
    cursor = connection.cursor()
    cursor.execute(
        raw_queries.LGA_NODES_QUERY, params=[state.lft, state.rgt])

    dataset = []
    while True:
        record = cursor.fetchone()
        if record is None:
            break

        if record[2].upper() == 'LGA':
            current_node = {
                k: v for k, v in zip(['id', 'name', 'type'], record)}
            current_node['children'] = []
            dataset.append(current_node)
        else:
            current_node['children'].append({
                k: v for k, v in zip(['id', 'name', 'type'], record)
            })

    sort_key = itemgetter('name')
    for lga_node in dataset:
        lga_node['children'] = sorted(lga_node['children'], key=sort_key)

    lga_nodes = sorted(dataset, key=sort_key)
    return lga_nodes


def generate_report_attachment(report):
    headers = [
        'name', 'girls_below1', 'girls_1to4', 'girls_5to9',
        'girls_10to18', 'boys_below1', 'boys_1to4', 'boys_5to9',
        'boys_10to18', 'estimate', 'u1_estimate', 'u5_estimate',
        'prior_u1', 'u1_performance', 'u5_performance',
        'reporting_centre_count', 'centre_count']

    header_row = [
        'Name', 'Girls <1', 'Girls 1-4', 'Girls 5-9',
        'Girls 10+', 'Boys <1', 'Boys 1-4', 'Boys 5-9', 'Boys 10+',
        'Population Estimate', 'U1 Estimate', 'U5 Estimate', 'U1 (graduated)',
        'U1 Performance', 'U5 Performance', 'Centres Reporting',
        'Total Centres']

    with BytesIO() as file_buffer:
        writer = csv.DictWriter(file_buffer, headers, extrasaction='ignore')
        writer.writerow(dict(zip(headers, header_row)))

        for record in report['breakdown']:
            writer.writerow(record)
        writer.writerow(report['summary'])

        output_value = file_buffer.getvalue()

    return output_value
