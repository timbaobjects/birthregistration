# -*- coding: utf-8 -*-
from django.db import models
from django_mysql.models import JSONField

from locations.models import Location
from reporters.models import Reporter, PersistantConnection

FIELD_MAP = {
    u'AA': u'cert_male_under_7d',
    u'AB': u'cert_female_under_7d',
    u'AC': u'uncert_male_under_7d',
    u'AD': u'uncert_female_under_7d',
    u'BA': u'cert_male_7to28d',
    u'BB': u'cert_female_7to28d',
    u'BC': u'uncert_male_7to28d',
    u'BD': u'uncert_female_7to28d',
    u'CA': u'cert_male_1to12m',
    u'CB': u'cert_female_1to12m',
    u'CC': u'uncert_male_1to12m',
    u'CD': u'uncert_female_1to12m',
    u'DA': u'cert_male_1to4y',
    u'DB': u'cert_female_1to4y',
    u'DC': u'uncert_male_1to4y',
    u'DD': u'uncert_female_1to4y',
    u'EA': u'cert_male_5to14y',
    u'EB': u'cert_female_5to14y',
    u'EC': u'uncert_male_5to14y',
    u'ED': u'uncert_female_5to14y',
    u'FA': u'cert_male_15to24y',
    u'FB': u'cert_female_15to24y',
    u'FC': u'uncert_male_15to24y',
    u'FD': u'uncert_female_15to24y',
    u'GA': u'cert_male_25to44y',
    u'GB': u'cert_female_25to44y',
    u'GC': u'uncert_male_25to44y',
    u'GD': u'uncert_female_25to44y',
    u'HA': u'cert_male_45to64y',
    u'HB': u'cert_female_45to64y',
    u'HC': u'uncert_male_45to64y',
    u'HD': u'uncert_female_45to64y',
    u'JA': u'cert_male_above_65y',
    u'JB': u'cert_female_above_65y',
    u'JC': u'uncert_male_above_65y',
    u'JD': u'uncert_female_above_65y',
}


class DeathReport(models.Model):
	'''
	Represents a single death record.

	Each death record contains the number of certified and uncertified
	deaths, male and female, for each of the age groups below:
	- under 7D
	- 7 - 28D
	- 1 - 12M
	- 1 - 4Y
	- 5 - 14Y
	- 15 - 24Y
	- 25 - 44Y
	- 45 - 64Y
	- 65Y+
	...bringing this to a total of 36 individual data points per record.
	For this reason, we're using a JSONField (which requires MySQL 5.7+)
	'''
	location = models.ForeignKey(Location, related_name=u'death_reports')
	reporter = models.ForeignKey(Reporter, blank=True, null=True,
		related_name=u'death_reports')
	connection = models.ForeignKey(PersistantConnection, blank=True, null=True,
		related_name=u'death_reports')
	time = models.DateTimeField()
	data = JSONField()
