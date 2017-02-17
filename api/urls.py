# -*- coding: utf-8 -*-
from django.conf.urls import url

from locations import api as locations_api

urlpatterns = [
    url(r'^locations/(?P<pk>\d+)/?$', locations_api.LocationItemView.as_view(),
        name=u'location_detail'),
    url(r'^locations/?$', locations_api.LocationListView.as_view(),
        name=u'location_list'),
    url(r'^locations-typed/?$', locations_api.TypedLocationListView.as_view(),
        name=u'location_list_typed'),
]
