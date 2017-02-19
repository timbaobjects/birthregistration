#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4
from django.conf.urls import url
from locations.views import *

urlpatterns = [
    url(r'^center/new/?$', CenterCreationView.as_view(), name='center_add'),
    url(r'^centers/?$', CenterListView.as_view(), name='center_list'),
    url(r'^center/(?P<pk>\d+)/?$', CenterUpdateView.as_view(), name='center_edit'),
]
