# -*- coding: utf-8 -*-
from datetime import datetime, time

from django import forms
from django.utils.timezone import make_aware
import django_filters

from common.filters import LocationFilter
from locations.models import Location


class DeathReportFilter(django_filters.FilterSet):
    location = LocationFilter(queryset=Location.objects.filter())
    date_start = django_filters.DateFilter(name=u'date', lookup_expr=u'gte',
            widget=forms.DateInput(attrs={
                u'class': u'form-control mb-2 mr-sm-2 mb-sm-0',
                u'placeholder': u'start'}))
    date_end = django_filters.DateFilter(name=u'date', lookup_expr=u'lte',
            widget=forms.DateInput(attrs={
                u'class': u'form-control mb-2 mr-sm-2 mb-sm-0',
                u'placeholder': u'end'}))
