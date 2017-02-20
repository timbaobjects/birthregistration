# -*- coding: utf-8 -*-
from datetime import datetime, time

from django import forms
from django.utils.timezone import make_aware
import django_filters

from common.filters import LocationFilter
from locations.models import Location


class DateStartFilter(django_filters.DateFilter):
    def filter(self, qs, value):
        if value:
            limit = make_aware(datetime.combine(value, time.min))
            return qs.filter(time__gte=limit)

        return qs


class DateEndFilter(django_filters.DateFilter):
    def filter(self, qs, value):
        if value:
            limit = make_aware(datetime.combine(value, time.max))
            return qs.filter(time__lte=limit)

        return qs


class DeathReportFilter(django_filters.FilterSet):
    location = LocationFilter(queryset=Location.objects.filter())
    date_start = DateStartFilter(name=u'time', lookup_expr=u'date__gte',
            widget=forms.DateInput(attrs={
                u'class': u'form-control mb-2 mr-sm-2 mb-sm-0', u'placeholder': u'start'}))
    date_end = DateEndFilter(name=u'time', lookup_expr=u'date__lte',
            widget=forms.DateInput(attrs={
                u'class': u'form-control mb-2 mr-sm-2 mb-sm-0', u'placeholder': u'end'}))
