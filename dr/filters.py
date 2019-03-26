# -*- coding: utf-8 -*-
from django import forms
import django_filters

from common.filters import LocationFilter
from locations.models import Location


class DeathReportFilter(django_filters.FilterSet):
    location = LocationFilter(label='Location', queryset=Location.objects.all())
    date_start = django_filters.DateFilter(
        name=u'date', label='Start date', lookup_expr=u'gte',
        widget=forms.DateInput(attrs={
            u'class': u'form-control mb-2 mr-sm-2 mb-sm-0',
            u'placeholder': u'start'}))
    date_end = django_filters.DateFilter(
        name=u'date', label='End date', lookup_expr=u'lte',
        widget=forms.DateInput(attrs={
            u'class': u'form-control mb-2 mr-sm-2 mb-sm-0',
            u'placeholder': u'end'}))
