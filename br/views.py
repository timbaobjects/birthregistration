# vim: ai ts=4 sts=4 et sw=4
from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
from br.models import BirthRegistration
from br.filters import BirthRegistrationFilter
from br.forms import BirthRegistrationModelForm
from br.helpers import get_record_dataset, stringify
from br.exporter import export_records_3
from locations.forms import generate_edit_form
from locations.filters import CenterFilterSet
from locations.models import Location, LocationType
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max, Min
from django.http import (
    HttpResponse, HttpResponseNotFound, HttpResponseRedirect,
    HttpResponseNotAllowed, HttpResponseForbidden, HttpResponseBadRequest)
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.generic import ListView, UpdateView, DeleteView, TemplateView


def dashboardview(request, state=None, year=now().year, month=None):
    # set cumulative to True to retrieve records from UNIX timestamp 0 to date
    cumulative = 'cumulative' in request.GET
    year = int(year)
    month = int(month) if month else None

    # validation
    if state:
        location = get_object_or_404(Location, name__iregex=state.replace('-', '.'), type__name="State")
        group_list = ['lga', 'rc']
    else:
        location = Location.objects.get(code='ng')
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
        'location': location,
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

    return render(request, 'br/br_dashboard.html', context)


class ReportListView(ListView):
    context_object_name = 'reports'
    template_name = 'br/reports_list.html'
    paginate_by = settings.PAGE_SIZE
    page_title = 'Reports List'

    def get_queryset(self):
        return self.filter_set.qs.order_by('-time')

    def get_context_data(self, **kwargs):
        context = super(ReportListView, self).get_context_data(**kwargs)
        context['filter_form'] = self.filter_set.form
        context['page_title'] = self.page_title
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.report_filter = BirthRegistrationFilter
        return super(ReportListView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.filter_set = self.report_filter(request.POST,
            queryset=BirthRegistration.objects.all().select_related(),
            request=request)
        request.session['report_filter'] = self.filter_set.form.data
        return super(ReportListView, self).get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        initial_data = request.session.get('report_filter', None)
        self.filter_set = self.report_filter(initial_data,
            queryset=BirthRegistration.objects.all().select_related(),
            request=request)
        return super(ReportListView, self).get(request, *args, **kwargs)


class ReportEditView(UpdateView):
    template_name = 'br/report_edit.html'
    page_title = 'Edit Report'

    def get_object(self, queryset=None):
        return self.report

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.report = get_object_or_404(BirthRegistration, pk=kwargs['pk'])
        self.form_class = BirthRegistrationModelForm
        return super(ReportEditView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ReportEditView, self).get_context_data(**kwargs)
        context['report'] = self.report
        context['report_form'] = self.form_class(instance=self.report)
        context['page_title'] = self.page_title
        return context

    def get_success_url(self):
        return reverse('reports_list')


class ReportDeleteView(DeleteView):
    def get_object(self, queryset=None):
        return self.report

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.report = get_object_or_404(BirthRegistration, pk=kwargs['pk'])
        return super(ReportDeleteView, self).dispatch(*args, **kwargs)

    def get_success_url(self):
        return reverse('reports_list')


class FAQView(TemplateView):
    template_name = 'br/faq.html'
    page_title = 'Frequently Asked Questions'
