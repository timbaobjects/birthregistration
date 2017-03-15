# vim: ai ts=4 sts=4 et sw=4
from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
from br.models import BirthRegistration
from br.filters import BirthRegistrationFilter
from br.forms import BirthRegistrationModelForm, ReportDeleteForm
from br.helpers import get_record_dataset
from br.exporter import export_records_3
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from locations.forms import generate_edit_form
from locations.filters import CenterFilterSet
from locations.models import Location, LocationType
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.db.models import Max, Min
from django.http import (
    HttpResponse, HttpResponseNotFound, HttpResponseRedirect,
    HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest)
from django.shortcuts import get_object_or_404, render
from django.utils.http import is_safe_url
from django.utils.timezone import now
from django.views.generic import ListView, UpdateView, DeleteView, TemplateView

PROTECTED_VIEW_PERMISSION = u'br.change_birthregistration'


def dashboardview(request, state=None, year=now().year, month=None):
    # set cumulative to True to retrieve records from UNIX timestamp 0 to date
    cumulative = 'cumulative' in request.GET
    year = int(year)
    month = int(month) if month else None

    # validation
    if state:
        location = get_object_or_404(Location, name__iregex=state.replace('-', '.'), type__name="State")
        location_codes = dict(location.children.all().values_list('name', 'code'))
        group_list = ['lga', 'rc']
    else:
        location = Location.objects.get(code='ng')
        location_codes = dict(Location.objects.filter(type__name="State").values_list('name', 'code'))
        group_list = ['state']

    if month and (month > 12):
        return HttpResponseNotFound()

    if 'export' in request.GET:
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="{}-{}-{}.xlsx"'.format(location.name, year, month)

        response.write(export_records_3(location, year, month, format='xlsx'))
        return response

    dataframe = get_record_dataset(location, year, month, cumulative)
    dataframe_distribution = dataframe \
        .groupby(lambda x: x.to_period('M')).sum().sort()
    dataframe_coverage = dataframe \
        .groupby([dataframe.lga if state else dataframe.state, dataframe.index.to_period('M')]) \
        .sum()

    if cumulative:
        dataframe_summary = dataframe.groupby(group_list).sum().sort()
    else:
        if month:
            timestamp = datetime(year, month, 1)
            dataframe_summary = dataframe \
                .truncate(before=timestamp, after=timestamp + relativedelta(months=1) - relativedelta(seconds=1)) \
                .groupby(group_list).sum().sort()
        else:
            timestamp = datetime(year, 1, 1)
            dataframe_summary = dataframe \
                .truncate(before=timestamp, after=timestamp + relativedelta(years=1) - relativedelta(seconds=1)) \
                .groupby(group_list).sum().sort()

    br_time_span = BirthRegistration.objects.all().aggregate(time_min=Min('time'), time_max=Max('time'))
    year_range = range(br_time_span['time_min'].year, br_time_span['time_max'].year + 1)

    context = {
        'page_title': 'Birth Registration Statistics',
        'location': location,
        'location_codes': location_codes,
        'year': year,
        'year_range': year_range,
        'month_range': range(1, 13),
        'month': month,
        'cumulative': cumulative,
        'dataframe_distribution': dataframe_distribution,
        'dataframe_coverage': dataframe_coverage,
        'dataframe_summary': dataframe_summary,
        'states': Location.objects.filter(type__name='State').order_by('name').values_list('name', flat=True),
    }

    return render(request, 'br/dashboard.html', context)


class ReportListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    context_object_name = 'reports'
    model = BirthRegistration
    template_name = 'br/reports_list.html'
    ordering = (u'-time',)
    paginate_by = settings.PAGE_SIZE
    page_title = 'Reports List'
    permission_required = PROTECTED_VIEW_PERMISSION
    report_filter = BirthRegistrationFilter

    def get_context_data(self, **kwargs):
        context = super(ReportListView, self).get_context_data(**kwargs)
        context['filter_form'] = self.filter_set.form
        context['page_title'] = self.page_title
        return context

    def get_queryset(self):
        queryset = super(ReportListView, self).get_queryset()
        self.filter_set = self.report_filter(self.request.GET,
            queryset=queryset)

        return self.filter_set.qs


class ReportEditView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'br/report_edit.html'
    permission_required = PROTECTED_VIEW_PERMISSION
    page_title = 'Edit Report'
    model = BirthRegistration
    form_class = BirthRegistrationModelForm

    def get_context_data(self, **kwargs):
        context = super(ReportEditView, self).get_context_data(**kwargs)
        context['report'] = self.object
        context['report_form'] = context[u'form']
        context['page_title'] = self.page_title
        return context

    def get_success_url(self):
        return reverse('reports_list')


class ReportDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = BirthRegistration
    permission_required = PROTECTED_VIEW_PERMISSION

    def get_success_url(self):
        return reverse('reports_list')


class FAQView(TemplateView):
    template_name = 'br/faq.html'
    page_title = 'Frequently Asked Questions'


def br_report_delete(request):
    if request.method != u'POST':
        return HttpResponseNotAllowed([u'POST'])

    if not request.user.is_authenticated:
        return HttpResponseForbidden()

    if not request.user.has_perm(PROTECTED_VIEW_PERMISSION):
        return HttpResponseForbidden()

    form = ReportDeleteForm(request.POST)
    redirect_path = request.META.get(u'HTTP_REFERER', reverse(u'br:reports_list'))

    if form.is_valid():
        reports = form.cleaned_data.get(u'reports')
        reports.delete()

        if not is_safe_url(url=redirect_path, host=request.get_host()):
            redirect_path = reverse(u'br:reports_list')

    return HttpResponseRedirect(redirect_path)
