import django_filters
from .models import Location


class LGAFilter(django_filters.ChoiceFilter):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [['', '']] + list(Location.objects.filter(
            type__name='LGA').values_list('pk', 'name'))
        super(LGAFilter, self).__init__(*args, **kwargs)

    def filter(self, qs, value):
        if value:
            try:
                lga = Location.objects.get(pk=value)
            except Location.DoesNotExist:
                return qs.none()

            descendant_centers_pks = lga.get_descendants().filter(
                type__name='RC').values_list('pk', flat=True)
            return qs.filter(pk__in=descendant_centers_pks)

        return qs


class CenterFilterSet(django_filters.FilterSet):
    lga = LGAFilter('LGA')
