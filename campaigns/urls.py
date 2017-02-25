# -*- coding: utf-8 -*-
from django.conf.urls import url

from campaigns import views

urlpatterns = [
	url(r'^$', views.CampaignListView.as_view(), name=u'campaign_list'),
	url(r'^new/?$', views.CampaignCreateView.as_view(), name=u'campaign_new'),
]
