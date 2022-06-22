# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.conf import settings
from django.views.generic import ListView

from reporters.models import Reporter

PROTECTED_VIEW_PERMISSION = 'reporters.change_reporter'


class ReporterListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    context_object_name = 'reporters'
    model = Reporter
    ordering = ('-id',)
    page_title = 'Reporters'
    paginate_by = settings.PAGE_SIZE
    permission_required = PROTECTED_VIEW_PERMISSION
    template_name = 'reporters/reporter_list.html'

    def get_context_data(self, **kwargs):
        context = super(ReporterListView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title

        return context
