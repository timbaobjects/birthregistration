from django import forms
from br.models import BirthRegistration


class BirthRegistrationModelForm(forms.ModelForm):
    class Meta:
        model = BirthRegistration
        fields = ('girls_below1', 'girls_1to4', 'girls_5to9', 'girls_10to18',
                  'boys_below1', 'boys_1to4', 'boys_5to9', 'boys_10to18')
