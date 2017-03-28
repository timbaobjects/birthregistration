# -*- coding: utf-8 -*-
from django import forms

from locations.models import Location
from profiles.models import Profile


class ProfileAdminForm(forms.ModelForm):
    locations = forms.ModelMultipleChoiceField(
    	queryset=Location.objects.filter(type__name=u'State'))

    class Meta:
        model = Profile
        fields = (u'user', u'locations')
