# -*- coding: utf-8 -*-
from django.conf.urls import url

from vitalregpro.api.views import br as br_views
from vitalregpro.api.views import dr as dr_views
from vitalregpro.api.views import mnchw as mnchw_views


urlpatterns = [
    url(r'^br/centres/?$', br_views.CentreCreateView.as_view(), name='br_centre_create'),
    url(r'^br/locations/?$', br_views.LocationListView.as_view(), name='br_location_list'),
    url(r'^br/location-types/?$', br_views.br_location_types, name='br_location_type_list'),
    url(r'^br/reports/?$', br_views.BirthReportListCreateView.as_view(), name='br_report_list'),
]
