# -*- coding: utf-8 -*-
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from vitalregpro.api import serializers
from vitalregpro.models import (
    Campaign, Location, LocationType, NonCompliance, Report, Shortage)

MNCHW_LOCATION_TYPE_NAMES = ['country', 'state', 'lga', 'ward']


def _default_queryset():
    queryset = Location.objects.filter(
            type__name__iregex='({})'.format('|'.join(MNCHW_LOCATION_TYPE_NAMES))
        ).order_by('lft', 'code')

    return queryset


@swagger_auto_schema(method='get')
@api_view()
def mnchw_location_types(request):
    return JsonResponse({
        'types': MNCHW_LOCATION_TYPE_NAMES
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


class CampaignListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Campaign.objects.order_by('-start_date')
    serializer_class = serializers.CampaignSerializer

    # @swagger_auto_schema(
    #     manual_parameters=[list_in_param, list_month_param, list_year_param])
    def get(self, request, *args, **kwargs):
        return super(CampaignListCreateView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        # ancestor_code = self.request.query_params.get('in')
        # month = self.request.query_params.get('month')
        # year = self.request.query_params.get('year')

        queryset = super(CampaignListCreateView, self).get_queryset()
        # if year is None:
        #     return queryset.none()
        # else:
        #     queryset = queryset.filter(time__year=year)

        # if month:
        #     queryset = queryset.filter(time__month=month)

        # if ancestor_code:
        #     ancestor = Location.get_by_code(ancestor_code)
        #     if ancestor is None:
        #         return queryset.none()
        #     queryset = queryset.filter(
        #         location__lft__gte=ancestor.lft,
        #         location__rgt__lte=ancestor.rgt
        #     )

        return queryset


class MNCHWReportListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Report.objects.order_by('-time')
    serializer_class = serializers.MNCHWReportSerializer

    @swagger_auto_schema(
        manual_parameters=[list_in_param, list_month_param, list_year_param])
    def get(self, request, *args, **kwargs):
        return super(MNCHWReportListCreateView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        ancestor_code = self.request.query_params.get('in')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        queryset = super(MNCHWReportListCreateView, self).get_queryset()
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


class NonComplianceListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = NonCompliance.objects.order_by('-time')
    serializer_class = serializers.NonComplianceSerializer

    @swagger_auto_schema(
        manual_parameters=[list_in_param, list_month_param, list_year_param])
    def get(self, request, *args, **kwargs):
        return super(NonComplianceListCreateView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        ancestor_code = self.request.query_params.get('in')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        queryset = super(NonComplianceListCreateView, self).get_queryset()
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


class ShortageListCreateView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Shortage.objects.order_by('-time')
    serializer_class = serializers.ShortageSerializer

    @swagger_auto_schema(
        manual_parameters=[list_in_param, list_month_param, list_year_param])
    def get(self, request, *args, **kwargs):
        return super(ShortageListCreateView, self).get(request, *args, **kwargs)

    def get_queryset(self):
        ancestor_code = self.request.query_params.get('in')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        queryset = super(ShortageListCreateView, self).get_queryset()
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
