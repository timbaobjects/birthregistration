# -*- coding: utf-8 -*-
from django.conf.urls import url

from profiles.views import UserCreateView, UserListView, UserUpdateView

urlpatterns = [
    url(r'^$', UserListView.as_view(), name='users_list'),
    url(r'^new/?$', UserCreateView.as_view(), name='user_create'),
    url(r'^(?P<pk>\d+)/?$', UserUpdateView.as_view(), name='user_edit'),
]