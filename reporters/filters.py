# -*- coding: utf-8 -*-
import django_filters

from common.filters import LocationFilter
from locations.models import Location
from messagebox.filters import _normalize_number
from reporters.models import PersistantConnection, Reporter


class ReporterLocationFilter(LocationFilter):
    def filter(self, queryset, value):
        return queryset.filter(
            location__lft__gte=value.lft, location__rgt__lte=value.rgt)


class PhoneNumberFilter(django_filters.CharFilter):
    def filter(self, queryset, value):
        if value:
            number = _normalize_number(value)
            return queryset.filter(connections__many__identity=number)

        return queryset


class ReporterFilter(django_filters.FilterSet):
    location = ReporterLocationFilter(queryset=Location.objects.filter(
        type__name__in=['State', 'LGA', 'RC']
    ))
    phone_number = PhoneNumberFilter()

    class Meta:
        model = Reporter
        fields = ('location',)
