# vim: ai ts=4 sts=4 et sw=4
import csv
import json

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin, PermissionRequiredMixin)
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import connection
from django.db.models import (
    Case, Count, IntegerField, OuterRef, Subquery, When)
from django.forms.formsets import formset_factory
from django.http import (
    HttpResponse, HttpResponseRedirect, StreamingHttpResponse)
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.generic import ListView, FormView, TemplateView
from drf_yasg.utils import swagger_auto_schema
import pandas as pd

from django.conf import settings

from br.models import BirthRegistration
from locations import raw_queries
from locations.forms import (
    generate_edit_form, CenterCreationForm, NonReportingCentresFilterForm)
from locations.filters import CenterFilterSet
from locations.models import Facility, Location, LocationType


class CenterListView(LoginRequiredMixin, ListView):
    context_object_name = 'centers'
    page_title = 'Centers'
    paginate_by = settings.PAGE_SIZE
    template_name = 'locations/center_list.html'

    def get(self, request, *args, **kwargs):
        queryset = Location.objects.filter(type__name=u'RC')

        try:
            profile = request.user.profile
            queryset = profile.filter_locations(queryset)
        except ObjectDoesNotExist:
            pass

        self.filter_set = CenterFilterSet(
            request.GET,
            queryset=queryset.order_by('code'))

        return super(CenterListView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CenterListView, self).get_context_data(**kwargs)

        context['filter_form'] = self.filter_set.form
        context['page_title'] = self.page_title

        return context

    def get_queryset(self):
        return self.filter_set.qs


class CenterUpdateView(
        LoginRequiredMixin, PermissionRequiredMixin, FormView):
    permission_required = 'locations.edit_location'
    template_name = 'locations/center_edit.html'

    def get_context_data(self, **kwargs):
        context = super(CenterUpdateView, self).get_context_data(**kwargs)

        self.object = self.get_object()

        context['page_title'] = 'Edit center: {}'.format(self.object.name)
        context[u'location'] = self.object

        return context

    def get_object(self):
        pk = self.kwargs.get(u'pk', None)
        location = get_object_or_404(Location, pk=pk)

        return location

    def form_valid(self, form):
        center = Location.objects.get(pk=form.cleaned_data['id'])
        center.name = form.cleaned_data['name']
        center.code = form.cleaned_data['code']
        center.parent = get_object_or_404(Location, pk=form.cleaned_data['lga'])
        center.active = form.cleaned_data['active']
        center.save()
        center.facilities.update(
            code=center.code, name=center.name
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, form_class=None):
        return generate_edit_form(self.get_object())

    def get_queryset(self):
        return Location.objects.filter(type__name='RC')

    def get_success_url(self):
        return reverse('locations:center_list')

    def post(self, request, *args, **kwargs):
        form = generate_edit_form(self.get_object(), request.POST)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class CenterCreationView(
        LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    page_title = u'Create registration centers'
    permission_required = 'locations.add_location'
    template_name = u'locations/center_new.html'

    def get_context_data(self, **kwargs):

        states = Location.objects.filter(type__name=u'State').order_by(u'name')

        context = super(CenterCreationView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context['states_data'] = json.dumps([
            {'id': s.id, 'name': s.name}
            for s in states
        ])

        return context

    def post(self, request, *args, **kwargs):
        CenterForms = formset_factory(CenterCreationForm)

        center_forms = CenterForms(request.POST)

        center_type = LocationType.objects.get(name=u'RC')

        for form in center_forms:
            if form.is_valid():
                lga = form.cleaned_data.get(u'lga')
                name = form.cleaned_data.get(u'name')

                if Location.objects.filter(name=name, parent=lga).exists():
                    messages.warning(
                        request, u'The center {} already exists.'.format(name),
                        extra_tags=u'alert-warning')
                    continue

                last_rc_code = lga.children.filter(type__name=u'RC').order_by(
                    u'-code').first().code
                try:
                    next_rc_code = str(int(last_rc_code) + 1).zfill(9)
                except ValueError:
                    messages.error(
                        request, u'The center {} could not be added due to an error'.format(
                            name), extra_tags=u'alert-danger')
                    continue

                rc = Location.objects.create(
                    name=name, parent=lga, code=next_rc_code, type=center_type)
                Facility.objects.create(
                    name=rc.name, code=rc.code, location=rc)
                messages.success(
                    request, u'The center {} was successfully added.'.format(
                        name
                    ), extra_tags=u'alert-success')
            else:
                messages.error(
                    request, u'The center {} could not be added without a parent LGA'.format(
                        form[u'name'].value()), extra_tags=u'alert-danger')

        if center_forms.is_valid():
            return HttpResponseRedirect(reverse_lazy(u'locations:center_list'))

        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def render_to_response(self, context, **kwargs):
        kwargs.setdefault('content_type', self.content_type)

        return self.response_class(
            request=self.request,
            template=self.template_name,
            context=context,
            **kwargs
        )


@swagger_auto_schema(auto_schema=None)
def facilities(request):
    ng = Location.get_by_code('ng')
    ancestor_pk = request.GET.get('ancestor', ng.pk)

    facility_dataframe = pd.read_sql_query(
        raw_queries.FACILITY_QUERY, connection, params=[ancestor_pk])

    response = HttpResponse(content_type='text/csv')
    facility_dataframe.to_csv(response, encoding='UTF-8', index=False)

    return response



class CSVBuffer(object):
    def write(self, value):
        return value


def _get_rows(centres):
    yield ['Centre', 'Code', 'LGA', 'State', 'Active?', 'Last report date']

    for centre in centres:
        last_report_time = centre.latest_birth_report_time()
        yield [
            centre.name,
            centre.code,
            centre.parent.name,
            centre.parent.parent.name,
            'Yes' if centre.active else 'No',
            last_report_time.strftime('%d-%m-%Y') if last_report_time else 'N/A'
        ]


class NonReportingCentresView(LoginRequiredMixin, ListView):
    context_object_name = 'centres'
    page_title = 'Non-reporting centres'
    paginate_by = settings.PAGE_SIZE
    template_name = 'locations/non_reporting_centre_list.html'

    def get(self, request, *args, **kwargs):
        centres = self.get_queryset()

        year = request.GET.get('year') or None
        month = request.GET.get('month') or None

        if request.GET.get('export'):
            writer = csv.writer(CSVBuffer())
            response = StreamingHttpResponse((writer.writerow(row) for row in _get_rows(centres)), content_type='text/csv')
            filename = 'non-reporting-centres-{}-{}.csv'.format(
                year,
                str(month).zfill(2)
            )
            response['Content-Disposition'] = 'attachment; filename={}'.format(
                filename)
            
            return response
        
        return super(NonReportingCentresView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(NonReportingCentresView, self).get_context_data(**kwargs)

        context['page_title'] = self.page_title
        context['filter_form'] = self.filter_form
        context['year'] = self.request.GET.get('year') or now().year
        context['month'] = self.request.GET.get('month') or ''

        return context

    def get_queryset(self):
        self.filter_form = NonReportingCentresFilterForm(self.request.GET)
        if self.filter_form.is_valid():
            filter_data = self.filter_form.cleaned_data
        else:
            filter_data = {}

        filter_kwargs = {}
        year = filter_data.get('year') or now().year
        filter_kwargs['birthregistration_records__time__year'] = int(year)
        month = filter_data.get('month')
        if month:
            filter_kwargs['birthregistration_records__time__month'] = int(month)

        if len(filter_kwargs) == 0:
            centres = Location.objects.none()
        else:
            centres = Location.objects.filter(
                type__name='RC'
            ).annotate(
                cnt=Count(Case(When(then=1, **filter_kwargs)))
            ).filter(cnt=0)

        return centres
