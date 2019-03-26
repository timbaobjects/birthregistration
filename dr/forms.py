# -*- coding: utf-8 -*-
from collections import OrderedDict
from django import forms

from dr.models import DeathReport, FIELD_MAP


class BaseDeathReportForm(forms.ModelForm):
    class Meta:
        model = DeathReport
        fields = []


attributes = OrderedDict()

for key, value in sorted(FIELD_MAP.items()):
    label = u'({}) {}'.format(key, value)
    attributes[key] = forms.IntegerField(help_text=label, required=False)


DeathReportForm = type('DeathReportForm', (BaseDeathReportForm,), attributes)


class DeathReportDeleteForm(forms.Form):
    reports = forms.ModelMultipleChoiceField(
        queryset=DeathReport.objects.all(),
        required=False, widget=forms.CheckboxSelectMultiple)
