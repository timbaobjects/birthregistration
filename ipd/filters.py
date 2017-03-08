# -*- coding: utf-8 -*-
import django_filters

from common.filters import LocationFilter
from locations.models import Location


class CampaignRelatedFilter(django_filters.FilterSet):
	location = LocationFilter(queryset=Location.objects.filter(
		type__name__in=[u'State', u'LGA']))
	time = django_filters.DateRangeFilter()
