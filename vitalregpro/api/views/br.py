# -*- coding: utf-8 -*-
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from vitalregpro.api import serializers
from vitalregpro.models import BirthRegistration, Location, LocationType

BR_LOCATION_TYPE_NAMES = ['country', 'state', 'lga', 'rc']


def _default_queryset():
    queryset = Location.objects.filter(
            type__name__iregex='({})'.format('|'.join(BR_LOCATION_TYPE_NAMES))
        ).order_by('lft', 'code')

    return queryset


@swagger_auto_schema(method='get')
@api_view()
def br_location_types(request):
    return JsonResponse({
        'types': BR_LOCATION_TYPE_NAMES
    })


class LocationItemView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = _default_queryset()
    serializer_class = serializers.LocationSerializer


list_type_param = openapi.Parameter(
    'type', openapi.IN_QUERY, description='Location type',
    type=openapi.TYPE_STRING)
list_in_param = openapi.Parameter(
    'in', openapi.IN_QUERY, description='Ancestor location code',
    type=openapi.TYPE_STRING)
list_month_param = openapi.Parameter(
    'month', openapi.IN_QUERY, description='Month', type=openapi.TYPE_INTEGER)
list_year_param = openapi.Parameter(
    'year', openapi.IN_QUERY, description='Year', type=openapi.TYPE_INTEGER)


class LocationListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.LocationSerializer

    @swagger_auto_schema(manual_parameters=[list_in_param, list_type_param,])
    def get(self, request, *args, **kwargs):
        return super(LocationListView, self).get(request, *args, **kwargs)

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
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.LocationSerializer


class BirthReportListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = BirthRegistration.objects.order_by('-time')
    serializer_class = serializers.BirthReportSerializer

    @swagger_auto_schema(
        manual_parameters=[list_in_param, list_month_param, list_year_param])
    def get(self, request, *args, **kwargs):
        return super(BirthReportListCreateView, self).get(request, *args, **kwargs)

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
