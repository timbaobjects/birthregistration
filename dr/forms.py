# -*- coding: utf-8 -*-
from collections import OrderedDict
from django import forms

from dr.models import DeathReport, FIELD_MAP


class BaseDeathReportForm(forms.ModelForm):
    class Meta:
        model = DeathReport
        fields = []


attributes = OrderedDict()

for key, value in sorted(FIELD_MAP.iteritems()):
    attributes[key] = forms.IntegerField(key, help_text=value, required=False)


DeathReportForm = type('DeathReportForm', (BaseDeathReportForm,), attributes)
