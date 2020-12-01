# -*- coding: utf-8 -*-
from django.conf.urls import url

from .views import MessageListView

urlpatterns = [
    url(r'^$', MessageListView.as_view(), name='message_list'),
]
