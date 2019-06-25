# -*- coding: utf-8 -*-
from django.conf.urls import url

from campaigns import views
from ipd import views as ipd_views

urlpatterns = [
	url(r'^$', ipd_views.dashboard, name=u'dashboard'),
	url(r'^(?P<campaign_id>\d+)/(?P<location_id>\d+)/?$', ipd_views.dashboard,
		name=u'dashboard_detail'),
	url(r'^campaigns/?$', views.CampaignListView.as_view(), name=u'campaign_list'),
	url(r'^campaigns/new/?$', views.CampaignCreateView.as_view(), name=u'campaign_new'),
	url(r'^campaigns/(?P<campaign_id>\d+)/(?P<location_id>\d+)/reports/?$',
		ipd_views.ReportListView.as_view(), name=u'report_list'),
	url(r'^campaigns/(?P<pk>\d+)/?$',
		views.CampaignUpdateView.as_view(), name=u'campaign_update'),
	url(r'^reports/(?P<pk>\d+)/?$', ipd_views.ReportUpdateView.as_view(),
		name=u'report_update'),
]
