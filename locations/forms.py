from django import forms
from .models import Location


def generate_edit_form(location, data=None):
    state_choices = Location.objects.filter(type__name='state').values_list(
        'id', 'name')

    def clean_location_field(form, field_name, location_type):
        loc_id = form.cleaned_data[field_name]
        try:
            Location.objects.get(pk=loc_id, type__name=location_type)
        except Location.DoesNotExist:
            raise forms.ValidationError('Invalid {}'.format(location_type))

        return loc_id

    class CenterEditForm(forms.Form):
        id = forms.IntegerField(widget=forms.HiddenInput())
        name = forms.CharField(max_length=100)
        code = forms.CharField(max_length=100)
        state = forms.ChoiceField(choices=state_choices)
        lga = forms.IntegerField(widget=forms.HiddenInput())
        active = forms.BooleanField(required=False)

        def clean_lga(self):
            return clean_location_field(self, 'lga', 'LGA')

        def clean(self):
            cleaned_data = super(CenterEditForm, self).clean()
            code = cleaned_data.get('code')
            location = None
            try:
                location = Location.objects.get(code=code)
            except Location.DoesNotExist:
                pass

            if location and (location.pk != cleaned_data.get('id')):
                self._errors['code'] = self.error_class(
                    'Code already in use for an existing location')
                del cleaned_data['code']

            return cleaned_data

    if data is None:
        ancestors = location.get_ancestors()
        data = {
            'id': location.pk,
            'name': location.name,
            'code': location.code,
            'state': ancestors.get(type__name='State').pk,
            'lga': ancestors.get(type__name='LGA').pk,
            'active': location.active
        }

    return CenterEditForm(data)


class CenterGroupCreationForm(forms.Form):
    center_data = forms.CharField(widget=forms.HiddenInput())


class CenterCreationForm(forms.Form):
    name = forms.CharField()
    lga = forms.ModelChoiceField(queryset=Location.objects.filter(
        type__name=u'LGA'))
