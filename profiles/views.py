# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseRedirect)
from django.utils.http import is_safe_url
from django.views.generic import CreateView, ListView, UpdateView

from profiles.forms import UserCreateForm, UserDeleteForm, UserForm
from profiles.models import Profile

PROTECTED_VIEW_PERMISSION = 'auth.change_user'


def update_permissions(user, form_data):
    from br.models import BirthRegistration
    from dr.models import DeathReport
    from ipd.models import Report
    from locations.models import Location
    from reporters.models import Reporter

    br_report_content_type = ContentType.objects.get_for_model(
        BirthRegistration)
    dr_report_content_type = ContentType.objects.get_for_model(DeathReport)
    location_content_type = ContentType.objects.get_for_model(Location)
    mnchw_report_content_type = ContentType.objects.get_for_model(Report)
    reporter_content_type = ContentType.objects.get_for_model(Reporter)
    user_content_type = ContentType.objects.get_for_model(User)

    if form_data.get('can_add_locations'):
        permission = Permission.objects.get(
            codename='add_location',
            content_type=location_content_type,
        )
        user.user_permissions.add(permission)

    if form_data.get('can_change_br_reports'):
        permission = Permission.objects.get(
            codename='change_birthregistration',
            content_type=br_report_content_type,
        )
        user.user_permissions.add(permission)

    if form_data.get('can_change_dr_reports'):
        permission = Permission.objects.get(
            codename='change_deathreport',
            content_type=dr_report_content_type,
        )
        user.user_permissions.add(permission)

    if form_data.get('can_change_mnchw_reports'):
        permission = Permission.objects.get(
            codename='change_report',
            content_type=mnchw_report_content_type,
        )
        user.user_permissions.add(permission)

    if form_data.get('can_change_reporters'):
        permission = Permission.objects.get(
            codename='change_reporter',
            content_type=reporter_content_type,
        )
        user.user_permissions.add(permission)

    if form_data.get('can_change_users'):
        permission = Permission.objects.get(
            codename='change_user',
            content_type=user_content_type,
        )
        user.user_permissions.add(permission)

    user.save()


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
        context['delete_form'] = UserDeleteForm()
        return context


class UserCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = UserCreateForm
    model = User
    page_title = 'Create User'
    permission_required = PROTECTED_VIEW_PERMISSION
    template_name = 'backend/user_create.html'

    def form_valid(self, form):
        user = form.save()
        cleaned_data = form.cleaned_data
        user.set_password(cleaned_data.get('password'))

        if not user.is_superuser:
            update_permissions(user, cleaned_data)

        return HttpResponseRedirect(reverse('users:users_list'))

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
        user = form.save()
        cleaned_data = form.cleaned_data

        if cleaned_data.get('password'):
            user.set_password(cleaned_data.get('password'))

        if not user.is_superuser:
            update_permissions(user, cleaned_data)

        return HttpResponseRedirect(reverse('users:users_list'))

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        return context


def user_delete(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    form = UserDeleteForm(request.POST, user=request.user)
    redirect_path = request.META.get(
        'HTTP_REFERER', reverse('users:users_list'))

    if form.is_valid():
        users = form.cleaned_data.get('users')
        users.delete()

        messages.add_message(
            request,
            messages.SUCCESS,
            '<strong>Success!</strong> The selected users were deleted.'
        )

        if not is_safe_url(url=redirect_path, host=request.get_host()):
            redirect_path = reverse('users:users_list')

    return HttpResponseRedirect(redirect_path)
