# -*- coding: utf-8 -*-
from django import forms

from campaigns.models import Campaign


class CampaignCreateForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = (u'name', u'locations', u'start_date', u'end_date')
