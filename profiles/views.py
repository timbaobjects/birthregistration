# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic import CreateView, ListView, UpdateView

from profiles.forms import UserForm
from profiles.models import Profile

PROTECTED_VIEW_PERMISSION = 'auth.change_user'


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    context_object_name = 'users'
    model = User
    ordering = ('-pk',)
    page_title = 'Users'
    paginate_by = settings.PAGE_SIZE
    permission_required = PROTECTED_VIEW_PERMISSION
    template_name = 'backend/user_list.html'

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = UserForm
    model = User
    page_title = 'Create User'
    permission_required = PROTECTED_VIEW_PERMISSION
    template_name = 'backend/user_create.html'

    def form_valid(self, form):
        pass

    def get_context_data(self, **kwargs):
        context = super(UserCreateView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    form_class = UserForm
    model = User
    page_title = 'Edit User'
    permission_required = PROTECTED_VIEW_PERMISSION
    template_name = 'backend/user_edit.html'

    def form_valid(self, form):
        pass

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context
    
