# -*- coding: utf-8 -*-
from django.http import JsonResponse
from rest_framework import generics

from br import models
from br.api import filters, serializers
from br.api.utils import get_api_data


def dashboard(request):
    level = request.GET.get('level', 'country')
    try:
        year = int(request.GET.get('year'))
    except TypeError, ValueError:
        year = None
    try:
        month = int(request.GET.get('month'))
    except TypeError, ValueError:
        month = None

    return JsonResponse(get_api_data(level, year, month))


class BirthRecordsListView(generics.ListAPIView):
    filterset_class = filters.BirthReportListFilter
    queryset = models.BirthRegistration.objects.all()
    serializer_class = serializers.BirthReportSerializer

    def filter_queryset(self, queryset):
        filter_ = self.filterset_class(self.request.GET, queryset=queryset)

        return filter_.qs
