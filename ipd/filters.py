# -*- coding: utf-8 -*-
import django_filters

from common.filters import LocationFilter
from locations.models import Location


class CampaignRelatedFilter(django_filters.FilterSet):
    location = LocationFilter(
        label='Location', queryset=Location.objects.filter(
            type__name__in=[u'State', u'LGA']))
    start_date = django_filters.DateFilter(
        u'time', label='Start date', lookup_expr=u'gte')
    end_date = django_filters.DateFilter(
        u'time', label='End date', lookup_expr=u'lte')
