#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.conf.urls import url
from django.http import HttpResponseRedirect

from br import views
from br.api.views import dashboard as api_dashboard
from unicefng.backend import HttpBackendView

urlpatterns = [
    url(r'^incoming/', HttpBackendView.as_view(backend_name='polling')),
    url(r'^api/v1/?$', api_dashboard, name='api_dashboard'),
    url(r'^help/?$', views.FAQView.as_view(), name='help'),
    url(r'^projections/?$', views.ProjectionDashboardView.as_view(), name='projection'),
    url(r'^reports/?$', views.ReportListView.as_view(), name='reports_list'),
    url(r'^report/(?P<pk>\d+)/?$', views.ReportEditView.as_view(),
        name='report_edit'),
    url(r'^report/(?P<pk>\d+)/delete$', views.ReportDeleteView.as_view(),
        name='report_delete'),
    url(r'^reports/delete/?$', views.br_report_delete, name=u'rep_delete'),
    url(r'^map/?$', views.map_dashboard, name='map_dashboard'),

    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^(?P<year>\d+)/?$', views.dashboard, name='dashboard_with_year'),
    url(r'^(?P<year>\d+)/(?P<month>\d+)/?$', views.dashboard,
        name='dashboard_with_year_and_month'),
    url(r'^(?P<state>[a-z\-]+)/?$', views.dashboard,
        name='dashboard_with_state'),
    url(r'^(?P<state>[a-z\-]+)/(?P<year>\d+)/?$', views.dashboard,
        name='dashboard_with_state_and_year'),
    url(r'^(?P<state>[a-z\-]+)/(?P<year>\d+)/(?P<month>\d+)/?$', views.dashboard,
        name='dashboard_with_state_year_and_month'),
]
