# -*- coding: utf-8 -*-
from django import forms

from campaigns.models import Campaign
from locations.models import Location


class CampaignForm(forms.ModelForm):
    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(type__name__in=[u'LGA', u'State']),
        widget=forms.CheckboxSelectMultiple())

    start_date = forms.DateField(input_formats=['%d/%m/%Y'])
    end_date = forms.DateField(input_formats=['%d/%m/%Y'])

    class Meta:
        model = Campaign
        fields = (u'name', u'locations', u'start_date', u'end_date')
