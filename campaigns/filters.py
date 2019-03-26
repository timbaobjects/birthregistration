# -*- coding: utf-8 -*-
import django_filters

from locations.models import Location


class CampaignLocationFilter(django_filters.ModelChoiceFilter):
    def filter(self, qs, location):
        if location:
            return qs.filter(locations__pk=location.pk)

        return qs


class CampaignFilterSet(django_filters.FilterSet):
    location = CampaignLocationFilter(
        label='Location', queryset=Location.objects.filter(
            type__name=u'State').order_by(u'name'))
    start_date = django_filters.DateFilter(
        label='Start date', lookup_expr=u'gte')
    end_date = django_filters.DateFilter(label='End date', lookup_expr=u'lte')
