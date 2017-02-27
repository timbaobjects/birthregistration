# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.db.models import F
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView

from django.conf import settings

from campaigns.forms import CampaignCreateForm
from campaigns.models import Campaign


class BaseCampaignViewMixin(object):
	@method_decorator(login_required)
	def dispatch(self, request, *args, **kwargs):
		return super(BaseCampaignViewMixin, self).dispatch(request, *args, **kwargs)

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

    def get_queryset(self):
        queryset = super(CampaignListView, self).get_queryset()

        queryset = queryset.prefetch_related(u'locations').annotate(
            loc_name=F(u'locations__name'),
            loc_type=F(u'locations__type__name')).values(
            u'name', u'start_date', u'end_date', u'loc_name', u'loc_type')

        return queryset

