# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

register = template.Library()


@register.simple_tag
def query_param_replace(request, field, value):
    query_params = request.GET.copy()
    query_params[field] = value

    return '{}?{}'.format(request.path, query_params.urlencode())
