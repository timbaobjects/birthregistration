# -*- coding: utf-8 -*-
from collections import OrderedDict
from operator import add

from django.db.models import F, Sum

from ipd import models


def get_campaign_data(campaign, state):
	model_classes = [models.Report, models.NonCompliance, models.Shortage]
	reports, noncompliance_reports, shortage_reports = \
		[campaign.get_related_objects(cls,
			state).annotate(lga=F(u'location__parent__name'),
				ward=F(u'location__name')).order_by(u'lga', u'ward')
			for cls in model_classes]

	lgas = campaign.campaign_lgas(state)

	return reports, noncompliance_reports, shortage_reports, lgas


def get_vaccination_summary(reports, lgas):
	summary = OrderedDict()

	for lga in lgas:
		lga_data = summary.setdefault(lga, {
			u'name': lga.name,
			u'summary': [0] * len(models.Report.IM_COMMODITIES),
			u'wards': []
		})

		for ward in lga.children.filter(type__name=u'Ward'):
			ward_data = {u'name': ward.name}
			ward_subset = reports.filter(ward=ward.name)
			ward_data[u'summary'] = [
				ward_subset.filter(commodity=code).aggregate(total=Sum(u'immunized')).get(u'total', 0)
				for code, description in models.Report.IM_COMMODITIES
			]

			lga_data[u'wards'].append(ward_data)
			lga_data[u'summary'] = map(add, ward_data[u'summary'], lga_data[u'summary'])

	return summary.values()


def get_noncompliance_summary(noncompliance_reports, lgas):
	summary = []

	for lga in lgas:
		lga_subset = noncompliance_reports.filter(lga=lga.name)
		lga_data = {
			u'name': lga.name,
			u'summary': [
				lga_subset.filter(reason=code).aggregate(total=Sum(u'cases')).get(u'total')
				for code, description in models.NonCompliance.NC_REASONS
			]
		}

		summary.append(lga_data)

	return summary


def get_shortage_summary(shortage_reports, lgas):
	summary = []

	for lga in lgas:
		lga_subset = shortage_reports.filter(lga=lga.name)
		lga_data = {
			u'name': lga.name,
			u'summary': [
				lga_subset.filter(commodity=code).exists()
				for code, description in models.Shortage.SHORTAGE_COMMODITIES
			]
		}

		summary.append(lga_data)

	return summary
