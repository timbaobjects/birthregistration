# -*- coding: utf-8 -*-
import django_filters


class LocationFilter(django_filters.ModelChoiceFilter):
    def filter(self, qs, location):
        if location:
            descendant_locs = location.get_descendants(include_self=True)
            return qs.filter(location__in=descendant_locs)

        return qs
