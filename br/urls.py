#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.conf.urls import url
from django.http import HttpResponseRedirect
from br.views import *
from unicefng.backend import HttpBackendView

urlpatterns = [
    url(r'^incoming/', HttpBackendView.as_view(backend_name='polling')),

    #url(r'^(?P<prefix>(monthly)?)/?(?P<state>\d*)/?(?P<year>\d*)/?(?P<month>\d*)/?$', 'unicefng.br.views.dashboard'),
    #url(r'^data/?(?P<prefix>(monthly)?)/?(?P<state>\d*)/?(?P<year>\d*)/?(?P<month>\d*)/?$', 'unicefng.br.views.csv_download'),
    url(r'^faq/?$', FAQView.as_view(), name='faq'),
    url(r'^reports/?$', ReportListView.as_view(), name='reports_list'),
    url(r'^report/(?P<pk>\d+)/?$', ReportEditView.as_view(),
        name='report_edit'),
    url(r'^report/(?P<pk>\d+)/delete$', ReportDeleteView.as_view(),
        name='report_delete'),
    url(r'^reports/delete/?$', br_report_delete, name=u'rep_delete'),
    url(r'^/?$', dashboardview, name='dashboard'),
    url(r'^(?P<year>\d+)/?$', dashboardview, name='dashboard_with_year'),
    url(r'^(?P<year>\d+)/(?P<month>\d+)/?$', dashboardview,
        name='dashboard_with_year_and_month'),
    url(r'^(?P<state>[a-z\-]+)/?$', dashboardview,
        name='dashboard_with_state'),
    url(r'^(?P<state>[a-z\-]+)/(?P<year>\d+)/?$', dashboardview,
        name='dashboard_with_state_and_year'),
    url(r'^(?P<state>[a-z\-]+)/(?P<year>\d+)/(?P<month>\d+)/?$', dashboardview,
        name='dashboard_with_state_year_and_month'),
]
