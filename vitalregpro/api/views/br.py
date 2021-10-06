# -*- coding: utf-8 -*-
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import generics

from vitalregpro.api import serializers
from vitalregpro.models import BirthRegistration, Location, LocationType

BR_LOCATION_TYPE_NAMES = ['country', 'state', 'lga', 'rc']


def _default_queryset():
    queryset = Location.objects.filter(
            type__name__iregex='({})'.format('|'.join(BR_LOCATION_TYPE_NAMES))
        ).order_by('lft', 'code')

    return queryset


def br_location_types(request):
    return JsonResponse({
        'types': BR_LOCATION_TYPE_NAMES
    })


class LocationItemView(generics.RetrieveAPIView):
    queryset = _default_queryset()
    serializer_class = serializers.LocationSerializer


class LocationListView(generics.ListAPIView):
    serializer_class = serializers.LocationSerializer

    def get_queryset(self):
        queryset = _default_queryset()

        type_specs = self.request.query_params.getlist('type')
        if type_specs:
            rgx_expression = '({})'.format('|'.join(type_specs))
            queryset = queryset.filter(type__name__iregex=rgx_expression)

        ancestor_code = self.request.query_params.get('in')
        if ancestor_code:
            ancestor = Location.get_by_code(ancestor_code)
            if ancestor is None:
                queryset = queryset.none()
            else:
                queryset = queryset.filter(lft__gte=ancestor.lft, rgt__lte=ancestor.rgt)

        return queryset


class CentreCreateView(generics.CreateAPIView):
    serializer_class = serializers.LocationSerializer


class BirthReportListCreateView(generics.ListCreateAPIView):
    queryset = BirthRegistration.objects.order_by('-time')
    serializer_class = serializers.BirthReportSerializer

    def get_queryset(self):
        ancestor_code = self.request.query_params.get('in')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        queryset = super(BirthReportListCreateView, self).get_queryset()
        if year is None:
            return queryset.none()
        else:
            queryset = queryset.filter(time__year=year)

        if month:
            queryset = queryset.filter(time__month=month)

        if ancestor_code:
            ancestor = Location.get_by_code(ancestor_code)
            if ancestor is None:
                return queryset.none()
            queryset = queryset.filter(
                location__lft__gte=ancestor.lft,
                location__rgt__lte=ancestor.rgt
            )

        return queryset

