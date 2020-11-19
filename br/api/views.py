# -*- coding: utf-8 -*-
from django.http import JsonResponse

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
