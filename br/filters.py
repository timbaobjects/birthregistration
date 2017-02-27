import django_filters
from django import forms
from br.models import BirthRegistration
from locations.models import LocationType, Location

class LocationFilter(django_filters.ChoiceFilter):
    ''' LocationFilter enables filtering of submissions
    by any of the parent locations (including the exact location)
    of the submission.
    '''

    def __init__(self, *args, **kwargs):
        lt_qs = kwargs.pop('queryset', LocationType.objects.filter(name__in=['State', 'LGA']))
        displayed_location_types = lt_qs.values('pk', 'name')
        displayed_locations = Location.objects.filter(type__pk__in=[t['pk'] for t in displayed_location_types]) \
            .order_by('type', 'name').values('pk', 'type__name', 'name')
        filter_locations = {}
        for displayed_location in displayed_locations:
            filter_locations.setdefault(displayed_location['type__name'], [])\
                .append((displayed_location['pk'], displayed_location['name']))

        kwargs['choices'] = [["", ""]] + [[lt, filter_locations[lt]] for lt in filter_locations.keys()]
        super(LocationFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            try:
                location = Location.objects.get(pk=value)
                return qs.is_within(location)
            except Location.DoesNotExist:
                return qs.none()
        else:
            return qs


class BirthRegistrationFilter(django_filters.FilterSet):
    location = LocationFilter()
    start_time = django_filters.DateFilter(name='time', lookup_type='gte')
    end_time = django_filters.DateFilter(name='time', lookup_type='lte')

    class Meta:
        model = BirthRegistration
        fields = ['location', 'start_time', 'end_time']

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super(BirthRegistrationFilter, self).__init__(*args, **kwargs)
