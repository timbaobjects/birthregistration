# vim: ai ts=4 sts=4 et sw=4
from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
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
from django.views.generic import ListView, FormView, DeleteView, TemplateView


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


class CenterUpdateView(FormView):
    template_name = 'br/center_edit.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super(CenterUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CenterUpdateView, self).get_context_data(**kwargs)

        context['page_title'] = 'Edit center: {}'.format(self.object.name)

        return context

    def get_object(self):
        pk = self.kwargs.get(u'pk', None)
        location = get_object_or_404(Location, pk=pk)

        return location

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
