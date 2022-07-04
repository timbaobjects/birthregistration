# -*- coding: utf-8 -*-
from django.forms import ModelForm

from .models import Reporter


class ReporterEditForm(ModelForm):
    class Meta:
        model = Reporter
        fields = ('first_name', 'last_name', 'location')
