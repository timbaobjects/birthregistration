from __future__ import unicode_literals
from datetime import datetime
# import logging
from django import template
from django.conf import settings
from locations.models import Location
from br.helpers import memoize
from br.models import CensusResult

# logger = logging.getLogger(__name__)
register = template.Library()


@register.filter
def sum(datacolumn):
    return datacolumn.fillna(0).sum()


@register.filter
def ix(dataframe, index):
    if dataframe is None:
        return None
    try:
        subset = dataframe.ix[index]
        return subset
    except Exception:
        return None


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def br_default(value):
    val = str(value)
    if val.isdigit():
        return value
    else:
        return '-'


@memoize
def get_population_growth_estimate(parent_location, location_name, location_type, year, month=None):
    # subnodes = [node for node in parent_location.nx_descendants() if (node['name'] == location_name) and (node['type'] == location_type)]
    # if len(subnodes) == 0:
    #     return 0
    # loc_node = subnodes[0]

    current_loc = parent_location.get_descendants(include_self=True).get(name=location_name, type__name=location_type)
    df = CensusResult.get_dataframe()

    if df.empty:
        return 0

    subset = df[(df.year <= year) & (df.loc_id == current_loc.id)].sort(columns='year', ascending=False)
    # subset = df[(df.year <= year) & (df.loc_id == loc_node['id'])].sort(columns='year', ascending=False)

    if subset.empty:
        return 0

    part = subset.iloc[0]

    # annual_population = part['population'] * ((1 + (part['growth_rate'] / 100.0)) ** (year - part['year']))
    # if month:
    #     return int(round(annual_population / 12.0))
    # else:
    #     return annual_population
    if month:
        growth_rate = ((1 + part['growth_rate']) ** (1 / 12.0)) - 1
        exponent = (year - part['year'] - 1) + int(month)
    else:
        growth_rate = part['growth_rate']
        exponent = (year - part['year'])

    estimate = part['population'] * ((1 + (growth_rate / 100.0)) ** (exponent))
    return estimate


@register.simple_tag
def performance(dataframe, index, location, node_pk, year, month, category):
    if location.type.name == 'State':
        location_type = 'LGA'
    else:
        location_type = 'State'
    subloc = Location.objects.get(pk=node_pk)
    cr = CensusResult.objects.get(location=subloc)

    try:
        estimate = get_population_growth_estimate(location, index,
                                                  location_type, year, month)
        total = 0.0
        if location_type == 'State':
            if category == 'below1':
                numerator = dataframe.ix[index].ix[category]
                denominator = estimate * cr.under_1_rate * 0.01
                return numerator / denominator
            elif category == '1to4':
                numerator = dataframe.ix[index].ix[['below1', '1to4']].sum()
                denominator = estimate * cr.under_5_rate * 0.01
                return numerator / denominator
        else:
            if category == 'below1':
                numerator = dataframe.ix[index].sum()[category]
                denominator = estimate * cr.under_1_rate * 0.01
                return numerator / denominator
            elif category == '1to4':
                numerator = dataframe.ix[index].sum()[['below1', '1to4']].sum()
                denominator = estimate * cr.under_5_rate * 0.01
                return numerator / denominator
        return total
    except Location.DoesNotExist:
        # logger.exception('Could not find location to compute estimate for')
        return 0
    except KeyError:
        # logger.exception('KeyError in "performance" tag')
        return 0


@register.simple_tag
def performance_pct(*args, **kwargs):
    return '%.0f' % (performance(*args, **kwargs) * 100,)


@register.simple_tag
def performance_class(*args, **kwargs):
    p = performance(*args, **kwargs)
    if p >= 0.7:
        return 'label-success'
    elif 0.3 <= p < 0.7:
        return 'label-warning'
    else:
        return 'label-danger'


@register.simple_tag
def month_name(month_index):
    return datetime(2000, month_index, 1).strftime('%B')


@register.simple_tag
def age_distribution_values(dataframe, category):
    values = []
    for period in dataframe.index:
        # the time period is specified in epoch milliseconds
        values.append([int(period.strftime('%s')) * 1000, dataframe.ix[period][category]])

    return values


@register.filter
def dataframe_coverage_locations(df):
    return sorted(set([i[0] for i in df.index]))


@register.filter
def dataframe_coverage_period(df, location):
    return df.ix[(location)].index


@register.filter
def period_in_ms(period):
    return int(period.strftime('%s')) * 1000


@register.simple_tag
def coverage_performance(dataframe, dataframe_location, period, category, location, year, month=None):
    if location.type.name == 'State':
        location_type = 'LGA'
    else:
        location_type = 'State'

    try:
        estimate = get_population_growth_estimate(location, dataframe_location, location_type, year, month)
        return dataframe.ix[(dataframe_location, period)].ix[category] / (estimate * settings.POPULATION_RATIOS[category])
    except Location.DoesNotExist:
        return 0


@register.filter
def subnodes(node, type=None):
    return Location._subnodes(node, type)


def location_performance(location, dataframe, year, month, category):
    estimate = get_population_growth_estimate(location, location.name, location.type.name, year, month)
    census_result = CensusResult.objects.get(location=location)
    total = 0.0
    try:
        if category == 'below1':
            numerator = dataframe[category].sum()
            denominator = estimate * census_result.under_1_rate * 0.01
            total = numerator / denominator
        elif category == '1to4':
            numerator = dataframe[['below1', '1to4']].sum().sum()
            denominator = estimate * census_result.under_5_rate * 0.01
            total = numerator / denominator
        return total
    except Location.DoesNotExist:
        # logger.exception('Could not find location to compute estimate for')
        return 0
    except KeyError:
        # logger.exception('KeyError in "location_performance" tag')
        return 0


@register.simple_tag
def location_performance_pct(*args, **kwargs):
    return '%.0f' % (location_performance(*args, **kwargs) * 100)


@register.simple_tag
def location_performance_class(*args, **kwargs):
    p = location_performance(*args, **kwargs)
    if p >= 0.7:
        return 'label-success'
    elif 0.3 <= p < 0.7:
        return 'label-warning'
    else:
        return 'label-danger'
