# -*- coding: utf-8 -*-
from django.db.models import F

from ipd import models


def get_campaign_data(campaign, state):
	model_classes = [models.Report, models.NonCompliance, models.Shortage]
	reports, noncompliance_reports, shortage_reports = \
		[campaign.get_related_objects(cls,
			state).annotate(lga=F(u'location__parent__name'),
				ward=F(u'location__name')) for cls in model_classes]

	return reports, noncompliance_reports, shortage_reports
