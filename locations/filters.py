import django_filters
from .models import Location


class LGAFilter(django_filters.ModelChoiceFilter):
    def filter(self, qs, value):
        if value:
            descendant_centers_pks = value.get_descendants().filter(
                type__name='RC').values_list('pk', flat=True)
            return qs.filter(pk__in=descendant_centers_pks)

        return qs


class CenterFilterSet(django_filters.FilterSet):
    lga = LGAFilter(
        label='LGA', queryset=Location.objects.filter(type__name=u'LGA'))
