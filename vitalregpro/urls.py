# -*- coding: utf-8 -*-
from django.conf.urls import url
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from vitalregpro.api.views import br as br_views
from vitalregpro.api.views import dr as dr_views
from vitalregpro.api.views import mnchw as mnchw_views


schema_view = get_schema_view(
    openapi.Info(
        title='RapidSMS API',
        default_version='v2',
        description='API for interfacing with RapidSMS',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    url(r'^br/centres/?$', br_views.CentreCreateView.as_view(), name='br_centre_create'),
    url(r'^br/locations/?$', br_views.LocationListView.as_view(), name='br_location_list'),
    url(r'^br/location-types/?$', br_views.br_location_types, name='br_location_type_list'),
    url(r'^br/reports/?$', br_views.BirthReportListCreateView.as_view(), name='br_report_list'),
    url(r'^dr/locations/?$', dr_views.LocationListView.as_view(), name='dr_location_list'),
    url(r'^dr/location-types/?$', dr_views.dr_location_types, name='dr_location_type_list'),
    url(r'^dr/reports/?$', dr_views.DeathReportListCreateView.as_view(), name='dr_report_list'),
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
