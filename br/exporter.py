import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from itertools import product
import numpy as np
import pandas as pd
# tablib is needed because apart from CSV, pandas doesn't do much to support
# writing to in-memory buffers.
import tablib
from locations.models import Location
from br import helpers
from br.models import BirthRegistration


headers = ['Date', 'State', 'LGA', 'Boys < 1', 'Boys 1-4', 'Boys 5-9',
    'Boys 10-17', 'Girls < 1', 'Girls 1-4', 'Girls 5-9', 'Girls 10-17']


def get_location_subnodes(location):
    subnodes = location.nx_descendants(include_self=True)
    center_pks = [node['id'] for node in subnodes if node['type'] == 'RC']
    state_nodes = [node for node in subnodes if node['type'] == 'State']
    location_tree = {}
    for node in state_nodes:
        location_tree[node['name']] = [n['name'] for n in Location._subnodes(node, 'LGA')]

    return center_pks, location_tree


def export_records(location, year, month=None, cumulative=False, format=None):
    if month:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, 1) + relativedelta(months=1) - relativedelta(seconds=1)
    else:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 1, 1) + relativedelta(years=1) - relativedelta(seconds=1)

    if cumulative:
        start_date = datetime.fromtimestamp(0)

    center_pks, location_tree = get_location_subnodes(location)

    records = BirthRegistration.objects.filter(
        location__pk__in=center_pks,
        time__range=(start_date, end_date)
    ).values(
        'girls_below1', 'girls_1to4', 'girls_5to9', 'girls_10to18',
        'boys_below1', 'boys_1to4', 'boys_5to9', 'boys_5to9',
        'boys_10to18', 'location__parent__name',
        'location__parent__parent__name', 'time'
    )

    dataframe = pd.DataFrame(list(records))
    dataset = tablib.Dataset(headers=headers)

    if not dataframe.empty:
        dataframe = dataframe.set_index('time').sort() \
            .rename(columns={'location__name': 'rc',
                'location__parent__name': 'lga',
                'location__parent__parent__name': 'state'
            })

        df_export = dataframe.groupby([dataframe.index.to_period('M'), dataframe.state, dataframe.lga]).sum()

        dates = sorted(set([idx[0] for idx in df_export.index]))
        states = sorted(location_tree.keys())
        for state in states:
            lgas = sorted(location_tree[state])
            for m_index in product(dates, [state], lgas):
                row = [str(m_index[0]), m_index[1], m_index[2]]

                try:
                    row.extend(df_export.ix[m_index][[
                            'boys_below1', 'boys_1to4', 'boys_5to9', 'boys_10to18',
                            'girls_below1', 'girls_1to4', 'girls_5to9', 'girls_10to18',
                        ]])
                except KeyError:
                    row.extend(['-'] * 8)
                dataset.append(row)

    if format:
        return getattr(dataset, format, dataset.xlsx)
    else:
        return dataset.xlsx


def export_records_2(location, year, month=None, columns=None, format=None):
    '''This function requires pandas 0.15+'''
    dataframe = helpers.get_record_dataset(location, year, month)

    if dataframe.empty:
        return u''

    column_map_data = {
        u'boys_below1': u'Boys < 1',
        u'boys_1to4': u'Boys 1 to 4',
        u'boys_5to9': u'Boys 5 to 9',
        u'boys_10to18': u'Boys 10 to 17',
        u'girls_below1': u'Girls < 1',
        u'girls_1to4': u'Girls 1 to 4',
        u'girls_5to9': u'Girls 5 to 9',
        u'girls_10to18': u'Girls 10 to 17',
    }
    column_map_locs = {
        u'rc': u'RC',
        u'lga': u'LGA',
        u'state': u'State',
    }

    column_map = {}
    column_map.update(column_map_data)
    column_map.update(column_map_locs)

    dataframe = dataframe.rename(columns=column_map)
    columns = column_map_data.values() if columns is None else [column_map_data[c] for c in columns]

    if month:
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, 1) + relativedelta(months=1) - relativedelta(seconds=1)
    else:
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 1, 1) + relativedelta(years=1) - relativedelta(seconds=1)

    dataframe = dataframe.truncate(before=start_date, after=end_date)

    # TODO: ensure that only a country or a state is sent in here.
    if location.type.name == u'Country':
        column_spec = [u'State']
    elif location.type.name == u'State':
        column_spec = [u'LGA']
    descendant_locs = location.get_descendants().filter(
        type__name=column_spec[0]).order_by(u'name')

    pivot_table = pd.pivot_table(dataframe, index=dataframe.index.month, values=columns, columns=column_spec, aggfunc=[np.sum])

    # get the transpose
    export_df = pivot_table.T.loc[u'sum'].fillna(u'-')
 
    headers = [u''] + column_spec + [calendar.month_abbr[i] for i in export_df.columns.tolist()]

    dataset = tablib.Dataset(headers=headers)
    indexer = product(columns, list(descendant_locs.values_list(u'name', flat=True)))

    for index in indexer:
        try:
            row = export_df.ix[index].tolist()
        except KeyError:
            row = [u'-'] * export_df.shape[1]

        dataset.append(list(index) + row)

    if format:
        return getattr(dataset, format, dataset.csv)

    return dataset.csv

def export_records_3(location, year, month=None, format=None):
    dataframe, subnodes = helpers.get_performance_dataframe(location, year, month)

    old_columns = [
        u'sum_girls_below1',
        u'sum_girls_1to4',
        u'sum_girls_5to9',
        u'sum_girls_10to18',
        u'sum_boys_below1',
        u'sum_boys_1to4',
        u'sum_boys_5to9',
        u'sum_boys_10to18',
        u'under_1',
        u'1to4',
        u'above5',
    ]

    new_columns = [
        u'Girls < 1',
        u'Girls 1 to 4',
        u'Girls 5 to 9',
        u'Girls 10+',
        u'Boys < 1',
        u'Boys 1 to 4',
        u'Boys 5 to 9',
        u'Boys 10+',
        u'Total < 1',
        u'Total 1 to 4',
        u'Total 5+',
    ]

    sort_column = u''

    if location.type.name == u'Country':
        old_columns.insert(0, u'state')
        new_columns.insert(0, u'State')
        sort_column = u'state'
    elif location.type.name == u'State':
        old_columns.insert(0, u'lga')
        new_columns.insert(0, u'LGA')
        sort_column = u'lga'

    column_map = dict(zip(old_columns, new_columns))

    dataframe = dataframe.sort_values(sort_column).rename(columns=column_map)
    headers = new_columns + [u'U1 Performance', u'U5 Performance']

    dataset = tablib.Dataset(headers=headers)
    for record in dataframe.to_dict(orient=u'records'):
        record[u'U1 Performance'] = round(record[u'U1 Performance'], 2)
        record[u'U5 Performance'] = round(record[u'U5 Performance'], 2)
        dataset.append([record[col] for col in headers])

    if format:
        return getattr(dataset, format, dataset.csv)

    return dataset.csv
