# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin, PermissionRequiredMixin
from django.core.urlresolvers import reverse
from django.db.models import F
from django.views.generic import CreateView, ListView

from django.conf import settings

from campaigns.filters import CampaignFilterSet
from campaigns.forms import CampaignCreateForm
from campaigns.models import Campaign

PROTECTED_VIEW_PERMISSION = u'ipd.change_report'


class BaseCampaignViewMixin(LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = PROTECTED_VIEW_PERMISSION

    def get_context_data(self, **kwargs):
        context = super(BaseCampaignViewMixin, self).get_context_data(**kwargs)

        context[u'page_title'] = self.page_title

        return context


class CampaignCreateView(BaseCampaignViewMixin, CreateView):
    form_class = CampaignCreateForm
    page_title = u'Create new campaign'
    template_name = u'campaigns/campaign_new.html'

    def get_success_url(self):
        return reverse(u'campaigns:campaign_list')


class CampaignListView(BaseCampaignViewMixin, ListView):
    model = Campaign
    ordering = (u'-end_date',)
    page_title = u'Campaigns'
    paginate_by = settings.PAGE_SIZE
    template_name = u'campaigns/campaign_list.html'
    filter_class = CampaignFilterSet

    def get_context_data(self, **kwargs):
        context = super(CampaignListView, self).get_context_data(**kwargs)
        context[u'filter_form'] = self.filter.form

        return context

    def get_queryset(self):
        queryset = super(CampaignListView, self).get_queryset()

        self.filter = self.filter_class(self.request.GET, queryset=queryset)

        queryset = self.filter.qs.prefetch_related(u'locations').annotate(
            loc_pk=F(u'locations__pk'), loc_name=F(u'locations__name'),
            loc_type=F(u'locations__type__name')).values(u'pk', u'loc_pk',
            u'name', u'start_date', u'end_date', u'loc_name', u'loc_type')

        return queryset
