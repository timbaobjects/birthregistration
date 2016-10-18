# vim: ai ts=4 sts=4 et sw=4
from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
from br.models import BirthRegistration
from br.filters import BirthRegistrationFilter
from br.forms import BirthRegistrationModelForm, CenterGroupCreationForm
from br.helpers import get_record_dataset, stringify
from br.exporter import export_records_2
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

        response.write(export_records_2(location, year, month, format='xlsx'))
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


class CenterListView(ListView):
    context_object_name = 'centers'
    page_title = 'Centers'
    paginate_by = settings.PAGE_SIZE
    template_name = 'br/center_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CenterListView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.filter_set = CenterFilterSet(
            request.GET,
            queryset=Location.objects.filter(type__name='RC').order_by('code'))

        return super(CenterListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CenterListView, self).get_context_data(**kwargs)

        context['filter_form'] = self.filter_set.form
        context['page_title'] = self.page_title

        return context

    def get_queryset(self):
        return self.filter_set.qs


class CenterUpdateView(UpdateView):
    template_name = 'br/center_edit.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super(CenterUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CenterUpdateView, self).get_context_data(**kwargs)

        context['page_title'] = 'Edit center: {}'.format(self.object.name)

        return context

    def form_valid(self, form):
        center = Location.objects.get(pk=form.cleaned_data['id'])
        center.name = form.cleaned_data['name']
        center.code = form.cleaned_data['code']
        center.parent = Location.objects.get_object_or_404(
            pk=form.cleaned_data['lga'])
        center.active = form.cleaned_data['active']
        center.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class):
        return generate_edit_form(self.object)

    def get_queryset(self):
        return Location.objects.filter(type__name='RC')

    def get_success_url(self):
        return reverse('center_list')

    def post(self, request, *args, **kwargs):
        form = generate_edit_form(self.get_object(), request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class CenterCreationView(TemplateView):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CenterCreationView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        group_form = CenterGroupCreationForm()
        location_data = {
            s.name: list(s.get_children().values_list('name', flat=True))
            for s in Location.objects.filter(type__name='State')
        }

        context = self.get_context_data(**kwargs)
        context['group_form'] = group_form
        context['location_data'] = json.dumps(location_data)
        context['page_title'] = 'Create centers'

        self.template_name = 'br/center_create_get.html'

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        group_form = CenterGroupCreationForm(request.POST)
        self.template_name = 'br/center_create_post.html'

        context['page_title'] = 'Center creation results'

        if not group_form.is_valid():
            return HttpResponseForbidden()

        center_data = json.loads(group_form.cleaned_data['center_data'])

        if not isinstance(center_data, list):
            return HttpResponseBadRequest()

        if not center_data:
            context['creation_log'] = []
            return self.render_to_response(context)

        log = center_data[:]
        center_type = LocationType.objects.get(name='RC')

        for index, row in enumerate(center_data):
            try:
                lga = Location.objects.get(
                    name=stringify(row['lga']).strip(),
                    parent__name=stringify(row['state']).strip(),
                    type__name='LGA')
            except Location.DoesNotExist:
                log[index]['message'] = 'Invalid state or LGA'
                log[index]['success'] = False
                continue

            try:
                loc, created = Location.objects.get_or_create(
                    name=stringify(row['name']).strip(),
                    parent=lga,
                    code=stringify(row['code']).strip(),
                    type=center_type)
            except IntegrityError:
                log[index]['message'] = 'Code already in use'
                log[index]['success'] = False
                continue

            if created:
                log[index]['message'] = 'OK'
                log[index]['success'] = True
            else:
                log[index]['message'] = 'Center already exists'
                log[index]['success'] = False

        context['creation_log'] = log

        return self.render_to_response(context)

    def render_to_response(self, context, **kwargs):
        kwargs.setdefault('content_type', self.content_type)

        return self.response_class(
            request=self.request,
            template=self.template_name,
            context=context,
            **kwargs
        )
