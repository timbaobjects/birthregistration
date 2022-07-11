# -*- coding: utf-8 -*-
import django_filters
from django import forms

from common.filters import LocationFilter
from locations.models import Location
from messagebox.filters import _normalize_number
from reporters.models import PersistantConnection, Reporter, Role


class ReporterLocationFilter(LocationFilter):
    def filter(self, queryset, value):
        return queryset.filter(
            location__lft__gte=value.lft, location__rgt__lte=value.rgt)


class PhoneNumberFilter(django_filters.CharFilter):
    def filter(self, queryset, value):
        if value:
            number = _normalize_number(value)
            if number:
                return queryset.filter(connections_many__identity=number)
            return queryset.none()

        return queryset


class ReporterFilter(django_filters.FilterSet):
    location = ReporterLocationFilter(queryset=Location.objects.all())
    phone_number = PhoneNumberFilter()
    role = django_filters.ModelChoiceFilter(
        empty_label='[Select Role]',
        queryset=Role.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Reporter
        fields = ('location', 'role',)
