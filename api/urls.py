# -*- coding: utf-8 -*-
from django.conf.urls import url

from br.api import views as br_api
from locations import api as locations_api
from locations.views import facilities

urlpatterns = [
    url(r'^locations/(?P<pk>\d+)/?$', locations_api.LocationItemView.as_view(),
        name=u'location_detail'),
    url(r'^locations/?$', locations_api.LocationListView.as_view(),
        name=u'location_list'),
    url(r'^locations-typed/?$', locations_api.TypedLocationListView.as_view(),
        name=u'location_list_typed'),
    url(r'^facilities/?$', facilities, name='facilities'),
    url(r'^projection/?$', br_api.get_projection_data, name='projection'),
]
