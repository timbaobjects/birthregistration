# -*- coding: utf-8 -*-
from django_filters import rest_framework as filters

from locations.models import Location


class LocationFilter(filters.NumberFilter):
    def filter(self, queryset, value):
        if value:
            try:
                location = Location.objects.get(pk=value)
            except Location.DoesNotExist:
                return queryset.none()
        
            return queryset.is_within(location)
        
        return queryset


class DateFromFilter(filters.IsoDateTimeFilter):
    def filter(self, queryset, value):
        if value:
            return queryset.filter(time__gte=value)
        
        return queryset


class DateToFilter(filters.IsoDateTimeFilter):
    def filter(self, queryset, value):
        if value:
            return queryset.filter(time__lte=value)
        
        return queryset


class DateFilter(filters.DateFilter):
    def filter(self, queryset, value):
        if value:
            return queryset.filter(
                time__year=value.year,
                time__month=value.month,
                time__day=value.day,
            )
        
        return value


class BirthReportListFilter(filters.FilterSet):
    location = LocationFilter(field_name='location', label='location')
    time_frm = DateFromFilter(field_name='from', label='from')
    time_to = DateToFilter(field_name='to', label='to')
    date = DateFilter(field_name='date', label='date')
