# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic import ListView, UpdateView

from reporters.filters import ReporterFilter
from reporters.forms import ReporterEditForm
from reporters.models import Reporter

PROTECTED_VIEW_PERMISSION = 'reporters.change_reporter'


class ReporterListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    context_object_name = 'reporters'
    model = Reporter
    ordering = ('-id',)
    page_title = 'Reporters'
    paginate_by = settings.PAGE_SIZE
    permission_required = PROTECTED_VIEW_PERMISSION
    template_name = 'backend/reporter_list.html'

    def get_queryset(self):
        queryset = super(ReporterListView, self).get_queryset()
        self.filter_set = ReporterFilter(self.request.GET, queryset=queryset)
        return self.filter_set.qs

    def get_context_data(self, **kwargs):
        context = super(ReporterListView, self).get_context_data(**kwargs)
        context['filter_form'] = self.filter_set.form
        context['page_title'] = self.page_title

        return context


class ReporterEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    context_object_name = 'reporter'
    form_class = ReporterEditForm
    model = Reporter
    page_title = 'Edit Reporter'
    permission_required = PROTECTED_VIEW_PERMISSION
    template_name = 'backend/reporter_edit.html'

    def get_context_data(self, **kwargs):
        context = super(ReporterEditView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        reporter = context['reporter']
        context['parent_location_pk'] = reporter.location.parent.pk

        return context

    def get_success_url(self):
        return reverse('reporters:reporter_list')
