# -*- coding: utf-8 -*-
import django_filters

from common.filters import LocationFilter
from locations.models import Location


class CampaignRelatedFilter(django_filters.FilterSet):
	location = LocationFilter(queryset=Location.objects.filter(
		type__name__in=[u'State', u'LGA']))
	start_date = django_filters.DateFilter(u'time', lookup_type=u'gte')
	end_date = django_filters.DateFilter(u'time', lookup_type=u'lte')
