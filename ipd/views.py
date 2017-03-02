# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, render
from django_pandas.io import read_frame

from campaigns.models import Campaign
from ipd.models import Report
from locations.models import Location


def dashboard(request, campaign_id=None, location_id=None):
    context = {}
    lgas = None
    lga_data = {}

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
        reports = campaign.get_related_objects(Report, location).annotate(
            lga=F(u'location__parent__name'), ward=F(u'location__name'))
        # dataframe = read_frame(reports, [u'immunized', u'commodity', u'lga', u'ward'], index_col=u'time')
        lgas = campaign.campaign_lgas(location).order_by(u'name')

        for lga in lgas:
            the_data = [
                reports.filter(lga=lga.name,
                    commodity=code).aggregate(total=Sum(u'immunized')).get(u'total', None)
                for code, description in Report.IM_COMMODITIES
                # dataframe[lga == lga.name && commodity == code][u'immunized'].sum()
                # for code, description in Report.IM_COMMODITIES
            ]
            lga_data[lga.name] = the_data

    context[u'campaigns'] = campaign_qs
    context[u'lgas'] = lgas
    context[u'commodities'] = OrderedDict(Report.IM_COMMODITIES)
    context[u'vaccination_data'] = lga_data
    context[u'selected_campaign'] = campaign
    context[u'selected_location'] = location

    return render(request, u'campaigns/dashboard.html', context)