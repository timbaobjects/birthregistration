#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.conf.urls import url
from locations import views

urlpatterns = [
    url(r'^center/new/?$', views.CenterCreationView.as_view(), name='center_add'),
    url(r'^centers/?$', views.CenterListView.as_view(), name='center_list'),
    url(r'^non-reporting-centers/?$', views.NonReportingCentresView.as_view(), name='non_reporting_center_list'),
    url(r'^center/(?P<pk>\d+)/?$', views.CenterUpdateView.as_view(), name='center_edit'),
]
