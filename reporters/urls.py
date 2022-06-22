# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.ReporterListView.as_view(), name='reporter_list'),
]
