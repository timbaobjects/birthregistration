# vim: ai ts=4 sts=4 et sw=4
from datetime import datetime
import json
from dateutil.relativedelta import relativedelta
from locations.forms import generate_edit_form, CenterCreationForm
from locations.filters import CenterFilterSet
from locations.helpers import stringify
from locations.models import Location, LocationType
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Max, Min
from django.forms.formsets import formset_factory
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
    template_name = 'locations/center_list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(CenterListView, self).dispatch(*args, **kwargs)

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


class CenterUpdateView(FormView):
    template_name = 'locations/center_edit.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        self.object = self.get_object()
        return super(CenterUpdateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(CenterUpdateView, self).get_context_data(**kwargs)

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
    page_title = u'Create registration centers'
    template_name = u'locations/center_new.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CenterCreationView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        states = Location.objects.filter(type__name=u'State').order_by(u'name')

        context = super(CenterCreationView, self).get_context_data(**kwargs)
        context['page_title'] = self.page_title
        context[u'states'] = states

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
                    messages.warning(request, u'The center {} already exists.'.format(
                        name), extra_tags=u'alert-warning')
                    continue

                last_rc_code = lga.children.filter(type__name=u'RC').order_by(u'-code').first().code
                try:
                    next_rc_code = str(int(last_rc_code) + 1).zfill(9)
                except ValueError:
                    messages.error(request, u'The center {} could not be added due to an error'.format(
                        name), extra_tags=u'alert-danger')
                    continue

                Location.objects.create(name=name, parent=lga, code=next_rc_code,
                    type=center_type)
                messages.success(request, u'The center {} was successfully added.'.format(
                    name), extra_tags=u'alert-success')
            else:
                messages.error(request, u'The center {} could not be added without a parent LGA'.format(
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
