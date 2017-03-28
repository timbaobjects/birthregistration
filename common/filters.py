# -*- coding: utf-8 -*-
import django_filters


class LocationFilter(django_filters.ModelChoiceFilter):
    def filter(self, qs, location):
        if location:
            return qs.is_within(location)

        return qs
