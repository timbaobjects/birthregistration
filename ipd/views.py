# -*- coding: utf-8 -*-
from django.db.models import F
from django.shortcuts import get_object_or_404, render

from campaigns.models import Campaign
from ipd.models import Report
from locations.models import Location


def dashboard(request, campaign_id=None, location_id=None):
    context = {}

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

    context[u'campaigns'] = campaign_qs
    context[u'selected_campaign'] = campaign
    context[u'selected_location'] = location

    return render(request, u'campaigns/dashboard.html', context)