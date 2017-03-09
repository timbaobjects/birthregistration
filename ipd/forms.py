# -*- coding: utf-8 -*-
from django import forms

from ipd.models import Report, NonCompliance


class ReportForm(forms.ModelForm):
    class Meta:
        fields = (u'immunized',)
        model = Report
