# -*- coding: utf-8 -*-
from datetime import date

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (HttpResponse, HttpResponseForbidden,
    HttpResponseNotAllowed, HttpResponseRedirect)
from django.utils.http import is_safe_url
from django.shortcuts import render
from django.views.generic import ListView, UpdateView
from django.views.generic.edit import FormMixin

from django.conf import settings

from dr.filters import DeathReportFilter
from dr.forms import DeathReportForm, DeathReportDeleteForm
from dr.helpers import death_report_summary, compute_rankings, death_report_periods, death_report_period_url
from dr.models import DeathReport

PROTECTED_VIEW_PERMISSION = u'dr.change_deathreport'


def dashboard(request, year=None, month=None):
    context = {}
    qs = DeathReport.objects.all()
    if year and month:
        period = date(year=int(year), month=int(month), day=1)
        qs = qs.filter(date__year=period.year, date__month=period.month)
    else:
        period = None

    df = death_report_summary(qs)
    period_urls = map(
        lambda p: death_report_period_url(p),
        death_report_periods(DeathReport.objects.all()))

    if not df.empty:
        general_data = df.groupby('country').sum().astype('int')
        states_data = compute_rankings(df.groupby('state').sum()).astype('int')

        context = {
            'general_male':        general_data.ix[0]['general_male'],
            'general_female':      general_data.ix[0]['general_female'],
            'general_certified':   general_data.ix[0]['general_certified'],
            'general_uncertified': general_data.ix[0]['general_uncertified'],
            'general_childbirth':  general_data.ix[0]['general_childbirth'],
            'general_fevers':      general_data.ix[0]['general_fevers'],
            'general_accidents':   general_data.ix[0]['general_accidents'],
            'general_hiv':         general_data.ix[0]['general_hiv'],
            'general_others':      general_data.ix[0]['general_others'],

            'female_1':          general_data.ix[0]['female_1'],
            'female_4':          general_data.ix[0]['female_4'],
            'female_5':          general_data.ix[0]['female_5'],
            'female_childbirth': general_data.ix[0]['female_childbirth'],
            'female_fevers':     general_data.ix[0]['female_fevers'],
            'female_accidents':  general_data.ix[0]['female_accidents'],
            'female_hiv':        general_data.ix[0]['female_hiv'],
            'female_others':     general_data.ix[0]['female_others'],

            'male_1':         general_data.ix[0]['male_1'],
            'male_4':         general_data.ix[0]['male_4'],
            'male_5':         general_data.ix[0]['male_5'],
            'male_fevers':    general_data.ix[0]['male_fevers'],
            'male_accidents': general_data.ix[0]['male_accidents'],
            'male_hiv':       general_data.ix[0]['male_hiv'],
            'male_others':    general_data.ix[0]['male_others'],

            'period_urls': period_urls,
            'period': period,
        }

        context['states_data'] = []

        for state in sorted(states_data.index):
            data = {'state': state}
            data.update(states_data.ix[state])
            context['states_data'].append(data)

    return render(request, 'dr/dashboard.html', context)


@login_required
def delete_death_reports(request):
    if request.method != u'POST':
        return HttpResponseNotAllowed([u'POST'])

    if not request.user.has_perm(PROTECTED_VIEW_PERMISSION):
        return HttpResponseForbidden()

    form = DeathReportDeleteForm(request.POST)
    redirect_path = request.META.get(u'HTTP_REFERER', u'')

    if not is_safe_url(url=redirect_path, host=request.get_host()):
        redirect_path = reverse(u'dr:dr_report_list')

    if form.is_valid():
        reports = form.cleaned_data.get(u'reports')

        if reports.exists():
            reports.delete()

        messages.add_message(
            request,
            messages.SUCCESS,
            '<strong>Success!</strong> The reports were successfully deleted.')

    return HttpResponseRedirect(redirect_path)


class DeathReportListView(LoginRequiredMixin, PermissionRequiredMixin,
        FormMixin, ListView):
    form_class = DeathReportDeleteForm
    model = DeathReport
    page_title = u'Death reports'
    paginate_by = settings.PAGE_SIZE
    permission_required = PROTECTED_VIEW_PERMISSION
    ordering = (u'-pk')
    template_name = u'dr/report_list.html'

    def get_context_data(self, **kwargs):
        context = super(DeathReportListView, self).get_context_data(**kwargs)

        context[u'filter_form'] = self.filterset.form
        context[u'page_title'] = self.page_title

        return context

    def get_queryset(self):
        qs = super(DeathReportListView, self).get_queryset()
        self.filterset = DeathReportFilter(self.request.GET, queryset=qs)

        return self.filterset.qs


class DeathReportUpdateView(LoginRequiredMixin, PermissionRequiredMixin,
        UpdateView):
    context_object_name = u'report'
    form_class = DeathReportForm
    model = DeathReport
    permission_required = PROTECTED_VIEW_PERMISSION
    template_name = u'dr/report_edit.html'

    def form_valid(self, form):
        self.object.data.update(form.cleaned_data)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(DeathReportUpdateView, self).get_context_data(**kwargs)

        context[u'page_title'] = u'Edit {date} report for {location}'.format(
            date=self.object.date, location=self.object.location.name)

        return context

    def get_initial(self):
        return self.object.data

    def get_success_url(self):
        return reverse(u'dr:dr_report_list')
