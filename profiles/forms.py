# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from locations.models import Location
from profiles.models import Profile


class ProfileAdminForm(forms.ModelForm):
    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(type__name=u'State'))

    class Meta:
        model = Profile
        fields = (u'user', u'locations')


class UserForm(forms.ModelForm):
    locations = forms.ModelMultipleChoiceField(
        queryset=Location.objects.filter(type__name=u'State'))
    can_add_locations = forms.BooleanField(required=False)
    can_change_br_reports = forms.BooleanField(required=False)
    can_change_dr_reports = forms.BooleanField(required=False)
    can_change_mnchw_reports = forms.BooleanField(required=False)
    can_change_reporters = forms.BooleanField(required=False)

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'is_active',
            'is_superuser'
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.get('instance')
        if user is not None:
            initial_data = kwargs.get('initial', {}).copy()

            # set up locations for subscription
            try:
                profile = user.profile
            except ObjectDoesNotExist:
                profile = None

            if profile is not None:
                initial_data['locations'] = profile.locations

            # set up permissions
            initial_data['can_add_locations'] = user.has_perm('locations.add_location')
            initial_data['can_change_br_reports'] = user.has_perm('br.change_birthregistration')
            initial_data['can_change_dr_reports'] = user.has_perm('dr.change_deathreport')
            initial_data['can_change_mnchw_reports'] = user.has_perm('ipd.change_report')
            initial_data['can_change_reporters'] = user.has_perm('reporters.change_reporter')

            kwargs['initial'] = initial_data

        super(UserForm, self).__init__(*args, **kwargs)
