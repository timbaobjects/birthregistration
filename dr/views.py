# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.views.generic import ListView, UpdateView

from django.conf import settings

from dr.forms import DeathReportForm
from dr.helpers import death_report_summary, compute_rankings
from dr.models import DeathReport
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

def dashboard(request):
    context = {}
    df = death_report_summary(DeathReport.objects.all())

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
        }

        context['states_data'] = []

        for state in sorted(states_data.index):
            data = {'state': state}
            data.update(states_data.ix[state])
            context['states_data'].append(data)

    return render(request, 'dr/dashboard.html', context)


class DeathReportListView(ListView):
    model = DeathReport
    page_title = u'Death reports'
    paginate_by = settings.PAGE_SIZE
    ordering = (u'-pk')
    template_name = u'dr/report_list.html'

    def get_context_data(self, **kwargs):
        context = super(DeathReportListView, self).get_context_data(**kwargs)

        context[u'page_title'] = self.page_title

        return context


class DeathReportUpdateView(UpdateView):
    form_class = DeathReportForm
    model = DeathReport
    template_name = u'dr/report_edit.html'

    def form_valid(self, form):
        self.object.data.update(form.cleaned_data)
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(DeathReportUpdateView, self).get_context_data(**kwargs)

        context[u'page_title'] = u'Edit {date} report for {location}'.format(
            date=self.object.time.date(), location=self.object.location.name)

        return context

    def get_initial(self):
        return self.object.data

    def get_success_url(self):
        return reverse(u'dr_report_list')
