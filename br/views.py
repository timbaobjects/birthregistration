# vim: ai ts=4 sts=4 et sw=4
from datetime import datetime
from functools import partial
from io import BytesIO
import json

from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse, HttpResponseNotFound, HttpResponseRedirect,
    HttpResponseNotAllowed, HttpResponseForbidden)
from django.shortcuts import get_object_or_404, render, render_to_response
from django.utils.http import is_safe_url
from django.utils.timezone import make_aware
from django.views.generic import ListView, UpdateView, DeleteView, TemplateView
import pandas as pd

from br import utils
from br.models import BirthRegistration, CensusResult
from br.filters import BirthRegistrationFilter
from br.forms import BirthRegistrationModelForm, ReportDeleteForm
from locations.models import Location

PROTECTED_VIEW_PERMISSION = u'br.change_birthregistration'

columns = [
    'girls_below1',
    'girls_1to4',
    'girls_5to9',
    'girls_10to18',
    'u5_girls',
    'girls_five_plus',
    'boys_below1',
    'boys_1to4',
    'boys_5to9',
    'boys_10to18',
    'u5_boys',
    'boys_five_plus',
    'u1',
    'u5',
    'one_to_four',
    'five_plus',
    'estimate',
    'u1_estimate',
    'u5_estimate',
    'u1_performance',
    'u5_performance',
]


def _state_dashboard(request, location, year, month, cumulative):
    br_time_span = utils.get_reporting_range()
    year_range = range(br_time_span[0].year, br_time_span[1].year + 1)

    if year not in year_range:
        year = year_range[-1]
        month = None

    # whether or not cumulative data is requested, be sure to group
    # by the LGA and sum so we get data at the LGA level
    if cumulative:
        reporting_df = utils.extract_cumulative_records(location, year, month)
        grouped_reporting_df = reporting_df.groupby(['lga_id', 'lga'])
        grouped_sum_df = grouped_reporting_df.sum()
    else:
        reporting_df, prior_u1_df = utils.extract_reporting_records(
            location, year, month)

        if not reporting_df.empty:
            census_df = CensusResult.get_census_dataframe(year)
            grouped_reporting_df = reporting_df.groupby(['lga_id', 'lga'])
            grouped_sum_df = grouped_reporting_df.sum()

            # reset the index (at this point it's a tuple of both the LGA name and
            # ID)
            grouped_sum_df_reindexed = grouped_sum_df.reset_index()

            # create an estimate computation function
            estimator = partial(utils.compute_estimate, census_df, year, month)

            # use it to compute estimates, but set the index to the LGA ID column
            # before using it
            estimate_series = grouped_sum_df_reindexed.set_index('lga_id').apply(
                estimator, axis=1)

            # create a DataFrame from the data so we can merge it
            estimate_df = pd.DataFrame(
                estimate_series.tolist(),
                columns=['lga_id', 'estimate', 'u1_estimate', 'u5_estimate'])

            grouped_sum_df_reindexed = grouped_sum_df_reindexed.merge(
                estimate_df)

            # create a performance computation function
            perf_estimator = partial(
                utils.compute_performance, prior_u1_df.set_index('lga_id'))

            # use it to compute performance
            performance_series = grouped_sum_df_reindexed.set_index(
                'lga_id').apply(perf_estimator, axis=1)

            # create a DataFrame from the performance data
            performance_df = pd.DataFrame(
                performance_series.tolist(),
                columns=['lga_id', 'u1_performance', 'u5_performance', 'prior_u1'])

            grouped_sum_df_reindexed = grouped_sum_df_reindexed.merge(
                performance_df)

            # set the index back
            grouped_sum_df = grouped_sum_df_reindexed.set_index(['lga_id', 'lga'])
        else:
            extra_columns = ['lga_id', 'lga']
            grouped_sum_df = pd.DataFrame(columns=columns + extra_columns)
            grouped_reporting_df = grouped_sum_df.groupby(extra_columns)

    if 'export' in request.GET:
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="{}-{}-{}.xlsx"'.format(location.name, year, month)
        output_buffer = BytesIO()
        writer = pd.ExcelWriter(output_buffer, options={'remove_timezone': True})
        utils.export_dataset(grouped_sum_df.reset_index(), writer)
        response.write(output_buffer.getvalue())

        return response

    # context vars
    dashboard_data = []
    map_data = {}

    # some housekeeping
    lga_nodes = utils.get_state_subnodes(location)

    # populate context vars
    for lga_node in lga_nodes:
        is_header = True
        index = (lga_node['id'], lga_node['name'])
        try:
            lga_data = grouped_sum_df.loc[index].to_dict()
            lga_data['lga_id'] = index[0]
            lga_data['lga'] = index[1]
            
            dashboard_data.append((lga_data, is_header))
            if not cumulative:
                map_data[index[0]] = (
                    grouped_sum_df.loc[index]['u1_performance'],
                    grouped_sum_df.loc[index]['u5_performance'],
                )
        except KeyError:
            lga_data = {c: None for c in columns}
            lga_data['lga_id'] = index[0]
            lga_data['lga'] = index[1]
            dashboard_data.append((lga_data, is_header))

            if not cumulative:
                # no submitted data equals zero performance
                map_data[index[0]] = (0, 0)

        is_header = False
        try:
            group = grouped_reporting_df.get_group(index)

            for rc_node in lga_node['children']:
                subset = group[group['rc'] == rc_node['name']]

                if subset.empty:
                    rc_data = {c: None for c in columns}
                    rc_data['rc'] = rc_node['name']
                else:
                    rc_data = subset.iloc[0].to_dict()

                dashboard_data.append((rc_data, is_header))
        except KeyError:
            for rc_node in lga_node['children']:
                rc_data = {c: None for c in columns}
                rc_data['rc'] = rc_node['name']
                dashboard_data.append((rc_data, is_header))

    summary_data = reporting_df.sum().to_dict()

    if not cumulative and not reporting_df.empty:
        prior_u1 = grouped_sum_df['prior_u1'].sum()
        u1_estimate = grouped_sum_df['u1_estimate'].sum()
        u5_estimate = grouped_sum_df['u5_estimate'].sum()
        try:
            u1_performance = round(summary_data['u1'] * 100 / u1_estimate)
        except ZeroDivisionError:
            u1_performance = 0
        u5_performance = round(
            (summary_data['u5'] + prior_u1) * 100 / u5_estimate)
    else:
        u1_performance = None
        u5_performance = None

    context = {
        'cumulative': cumulative,
        'table_data': dashboard_data,
        'map_data': json.dumps(map_data),
        'summary_data': summary_data,
        'level': location.type.name.lower(),
        'u1_performance': u1_performance,
        'u5_performance': u5_performance,
        'location': location,
        'reporting_location_count': reporting_df['loc_count'].sum(),
        'states': Location.objects.filter(type__name='State').order_by(
            'name').values_list('name', flat=True),
        'year': year,
        'year_range': year_range[::-1],
        'month': month,
        'month_range': range(1, 13),
    }

    return render(request, 'br/dashboard.html', context)


def _country_dashboard(request, location, year, month, cumulative):
    state_nodes = utils.get_national_subnodes()
    br_time_span = utils.get_reporting_range()
    year_range = range(br_time_span[0].year, br_time_span[1].year + 1)

    if year not in year_range:
        year = year_range[-1]
        month = None

    if cumulative:
        reporting_df = utils.extract_cumulative_records(location, year, month)
    else:
        reporting_df, prior_u1_df = utils.extract_reporting_records(
            location, year, month)

        if not reporting_df.empty:
            census_df = CensusResult.get_census_dataframe(year)

            estimator = partial(utils.compute_estimate, census_df, year, month)

            estimate_series = reporting_df.set_index('state_id').apply(
                estimator, axis=1)
            estimate_df = pd.DataFrame(
                estimate_series.tolist(),
                columns=['state_id', 'estimate', 'u1_estimate', 'u5_estimate'])

            reporting_df = reporting_df.merge(estimate_df)

            perf_estimator = partial(
                utils.compute_performance, prior_u1_df.set_index('state_id'))

            performance_series = reporting_df.set_index('state_id').apply(
                perf_estimator, axis=1)

            performance_df = pd.DataFrame(
                performance_series.tolist(),
                columns=['state_id', 'u1_performance', 'u5_performance', 'prior_u1'])

            reporting_df = reporting_df.merge(performance_df)

    if 'export' in request.GET:
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="{}-{}-{}.xlsx"'.format(location.name, year, month)
        output_buffer = BytesIO()
        writer = pd.ExcelWriter(output_buffer, options={'remove_timezone': True})
        utils.export_dataset(reporting_df.reset_index(), writer)
        response.write(output_buffer.getvalue())

        return response

    dashboard_data = []
    map_data = {}
    reporting_df_reindexed = reporting_df.set_index('state_id')
    for state_node in state_nodes:
        try:
            row = reporting_df_reindexed.loc[state_node['id']]
            dashboard_data.append(row.to_dict())
            if not cumulative:
                map_data[state_node['id']] = (
                    row['u1_performance'], row['u5_performance'])
        except KeyError:
            row = {'state': state_node['name']}
            dashboard_data.append(row)
            if not cumulative:
                map_data[state_node['id']] = (0, 0)

    summary_data = reporting_df.sum().to_dict()

    if not cumulative and not reporting_df.empty:
        u1_performance = round(
            summary_data['u1'] * 100 / summary_data['u1_estimate'])
        u5_performance = round(
            (summary_data['u5'] + summary_data['prior_u1']) * 100 / summary_data['u5_estimate'])
    else:
        u1_performance = None
        u5_performance = None

    context = {
        'cumulative': cumulative,
        'table_data': dashboard_data,
        'map_data': json.dumps(map_data),
        'summary_data': summary_data,
        'level': location.type.name.lower(),
        'u1_performance': u1_performance,
        'u5_performance': u5_performance,
        'location': location,
        'reporting_location_count': reporting_df['loc_count'].sum(),
        'states': Location.objects.filter(type__name='State').order_by(
            'name').values_list('name', flat=True),
        'year': year,
        'year_range': year_range[::-1],
        'month': month,
        'month_range': range(1, 13),
    }

    return render(request, 'br/dashboard.html', context)


def dashboard(request, state=None, year=None, month=None):
    if state is None:
        location = Location.get_by_code('ng')
    else:
        location = get_object_or_404(
            Location, name__iregex=state.replace('-', '.'), type__name="State")

    # sanity checks
    try:
        year = int(year) if year else make_aware(datetime.now()).year
        month = int(month) if month else None
    except ValueError:
        return HttpResponseNotFound()

    if month and (month > 12):
        return HttpResponseNotFound()

    cumulative = 'cumulative' in request.GET
    if state:
        return _state_dashboard(request, location, year, month, cumulative)
    else:
        return _country_dashboard(request, location, year, month, cumulative)

def map_dashboard(request):
    return render_to_response('br/map_dashboard.html')


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
        queryset = queryset.filter_supervised_locations(self.request.user)
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
        return reverse('br:reports_list')


class ReportDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = BirthRegistration
    permission_required = PROTECTED_VIEW_PERMISSION

    def get_success_url(self):
        return reverse('br:reports_list')


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

        messages.add_message(
            request,
            messages.SUCCESS,
            '<strong>Success!</strong> The reports were successfully deleted.')

        if not is_safe_url(url=redirect_path, host=request.get_host()):
            redirect_path = reverse(u'br:reports_list')

    return HttpResponseRedirect(redirect_path)


class ProjectionDashboardView(TemplateView):
    template_name = 'br/projection.html'
    page_title = 'Projections'

    def get_context_data(self, **kwargs):
        context = super(ProjectionDashboardView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title

        locations = Location.objects.filter(
            type__name__in=('Country', 'State')
        ).order_by(
            'level', 'name'
        ).values('id', 'name')

        start_year, end_year = utils.get_report_year_range()
        
        context['locations'] = json.dumps(list(locations))
        context['year_range'] = json.dumps(range(start_year, end_year + 1))

        return context
