# -*- coding: utf-8 -*-
from collections import OrderedDict
from itertools import groupby
import json

from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from django.conf import settings

from campaigns.models import Campaign
from ipd.filters import CampaignRelatedFilter
from ipd.helpers import get_campaign_data
from ipd.models import NonCompliance, Report, Shortage
from locations.models import Location


def dashboard(request, campaign_id=None, location_id=None):
    context = {}
    lgas = None
    vaccination_data = {}
    noncompliance_data = {}
    shortage_data = {}
    chart_data = []

    if campaign_id and location_id:
        campaign = get_object_or_404(Campaign, pk=campaign_id)
        location = get_object_or_404(Location, pk=location_id)
        context[u'page_title'] = u'{name} ({location_name} ({location_type})'.format(
            name=campaign.name, location_name=location.name, location_type=location.type.name)
    else:
        campaign = location = None
        context[u'page_title'] = u'MNCHW'

    campaign_qs = Campaign.objects.order_by(
        u'-start_date').prefetch_related(u'locations').annotate(
            loc_name=F(u'locations__name'),
            loc_type=F(u'locations__type__name'),
            loc_pk=F(u'locations__pk')
        ).filter(loc_type='State').values(
        u'name', u'loc_name', u'loc_type', u'loc_pk', u'pk')

    if campaign:
        reports, noncompliance_reports, shortages = get_campaign_data(campaign, location)
        lgas = campaign.campaign_lgas(location).order_by(u'name')

        for lga in lgas:
            lga_summary = [
                reports.filter(lga=lga.name,
                    commodity=code).aggregate(total=Sum(u'immunized')).get(u'total')
                for code, description in Report.IM_COMMODITIES
            ]
            vaccination_data[lga.name] = lga_summary

            lga_noncompliance_summary = [
                noncompliance_reports.filter(lga=lga.name,
                    reason=reason).aggregate(total=Sum(u'cases')).get(u'total')
                for reason, description in NonCompliance.NC_REASONS
            ]
            noncompliance_data[lga.name] = lga_noncompliance_summary

            lga_shortage_summary = [
                shortages.filter(lga=lga.name, commodity=commodity).exists()
                for commodity, description in Shortage.SHORTAGE_COMMODITIES
            ]

            shortage_data[lga.name] = lga_shortage_summary

        chart_data.append([u'x'] + [d.strftime(u'%Y-%m-%d') for d in reports.values_list(u'time', flat=True).distinct().order_by(u'time')])
        extracted_data = list(reports.values(u'time', u'commodity').annotate(total=Sum(u'immunized')).order_by(u'commodity', u'time'))
        for commodity, group in groupby(extracted_data, lambda r: r.get(u'commodity')):
            row = [commodity.upper()] + [i.get('total') for i in sorted(group, key=lambda s: s.get('time'))]
            chart_data.append(row)

    context[u'chart_data'] = json.dumps(chart_data)
    context[u'campaigns'] = campaign_qs
    context[u'lgas'] = lgas
    context[u'commodities'] = OrderedDict(Report.IM_COMMODITIES)
    context[u'nc_reasons'] = OrderedDict(NonCompliance.NC_REASONS)
    context[u'shortage_commodities'] = OrderedDict(Shortage.SHORTAGE_COMMODITIES)
    context[u'vaccination_data'] = vaccination_data
    context[u'noncompliance_data'] = noncompliance_data
    context[u'shortage_data'] = shortage_data
    context[u'selected_campaign'] = campaign
    context[u'selected_location'] = location

    return render(request, u'campaigns/dashboard.html', context)


class CampaignRelatedObjectListMixin(object):
    paginate_by = settings.PAGE_SIZE

    def get_campaign(self):
        campaign_id = self.kwargs.get(u'campaign_id')

        campaign = get_object_or_404(Campaign, pk=campaign_id)

        return campaign

    def get_context_data(self, **kwargs):
        context = super(CampaignRelatedObjectListMixin, self).get_context_data(**kwargs)

        context[u'filter_form'] = self.filterset.form

        return context

    def get_queryset(self):
        campaign = self.get_campaign()
        model_class = self.model
        queryset = model_class.objects.filter(
            time__range=(campaign.start_date, campaign.end_date))

        # add in the filter
        self.filterset = CampaignRelatedFilter(self.request.GET, queryset=queryset)

        return self.filterset.qs


class ReportListView(CampaignRelatedObjectListMixin, ListView):
    model = Report
    template_name = u'ipd/report_list.html'


class NonComplianceReportListView(CampaignRelatedObjectListMixin, ListView):
    model = NonCompliance
    template_name = u'ipd/nc_report_list.html'


class ShortageReportListView(CampaignRelatedObjectListMixin, ListView):
    model = Shortage
    template_name = u'ipd/shortage_report_list.html'
