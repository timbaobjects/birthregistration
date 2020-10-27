# -*- coding: utf-8 -*-
from django.db.models import Q
from rest_framework import generics

from locations.api.serializers import (
    LocationSerializer, RegistrationCentreSerializer)
from locations.models import Location


class LocationItemView(generics.RetrieveAPIView):
    '''
    Retrieves a single location
    '''
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_queryset(self):
        queryset = super(LocationListView, self).get_queryset()

        # filter on prefix (for name-based lookups)
        prefix = self.request.query_params.get(u'q', None)
        if prefix:
            queryset = queryset.filter(name__istartswith=prefix)

        return queryset


class TypedLocationListView(LocationListView):
    def get_queryset(self):
        queryset = super(TypedLocationListView, self).get_queryset()

        # type is required
        # this works without case sensitivity on MySQL
        # TODO: implement explicit case-insensitivity
        type_names = self.request.query_params.get(u'type')
        if not type_names:
            return queryset.none()

        types = type_names.split(u',')
        query = Q()
        for t in types:
            query.add(Q(type__name__iexact=t), Q.OR)
        queryset = queryset.filter(query)

        # filter on parent id
        parent_id = self.request.query_params.get(u'parent')
        if parent_id:
            queryset = queryset.filter(parent=parent_id)

        return queryset


class CentreListView(generics.ListAPIView):
    queryset = Location.objects.filter(type__name='RC')
    serializer_class = RegistrationCentreSerializer

    def filter_queryset(self, queryset):
        location_pk = self.request.GET.get('location')
        if location_pk is not None:
            try:
                location = Location.objects.get(pk=location_pk)
            except Location.DoesNotExist:
                return queryset.none()
            
            return queryset.filter(
                lft__gte=location.lft,
                rgt__lte=location.rgt
            )

        return queryset
