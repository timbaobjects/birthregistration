# -*- coding: utf-8 -*-
from django.db import models
from django_mysql.models import JSONField

from locations.models import Location
from reporters.models import Reporter, PersistantConnection

FIELD_MAP = {
    u'AA': u'Number of certified deaths of males under 7 days old',
    u'AB': u'Number of certified deaths of females under 7 days old',
    u'AC': u'Number of uncertified deaths of males under 7 days old',
    u'AD': u'Number of uncertified deaths of females under 7 days old',
    u'BA': u'Number of certified deaths of males 7-28 days old',
    u'BB': u'Number of certified deaths of females 7-28 days old',
    u'BC': u'Number of uncertified deaths of males 7-28 days old',
    u'BD': u'Number of uncertified deaths of females 7-28 days old',
    u'CA': u'Number of certified deaths of males 1 to 12 months old',
    u'CB': u'Number of certified deaths of females 1 to 12 months old',
    u'CC': u'Number of uncertified deaths of males 1 to 12 months old',
    u'CD': u'Number of uncertified deaths of females 1 to 12 months old',
    u'DA': u'Number of certified deaths of males 1 to 4 years old',
    u'DB': u'Number of certified deaths of females 1 to 4 years old',
    u'DC': u'Number of uncertified deaths of males 1 to 4 years old',
    u'DD': u'Number of uncertified deaths of females 1 to 4 years old',
    u'EA': u'Number of certified deaths of males 5 to 14 years old',
    u'EB': u'Number of certified deaths of females 5 to 14 years old',
    u'EC': u'Number of uncertified deaths of males 5 to 14 years old',
    u'ED': u'Number of uncertified deaths of females 5 to 14 years old',
    u'FA': u'Number of certified deaths of males 15 to 24 years old',
    u'FB': u'Number of certified deaths of females 15 to 24 years old',
    u'FC': u'Number of uncertified deaths of males 15 to 24 years old',
    u'FD': u'Number of uncertified deaths of females 15 to 24 years old',
    u'GA': u'Number of certified deaths of males 25 to 44 years old',
    u'GB': u'Number of certified deaths of females 25 to 44 years old',
    u'GC': u'Number of uncertified deaths of males 25 to 44 years old',
    u'GD': u'Number of uncertified deaths of males 25 to 44 years old',
    u'HA': u'Number of certified deaths of males 45 to 64 years old',
    u'HB': u'Number of certified deaths of females 45 to 64 years old',
    u'HC': u'Number of uncertified deaths of males 45 to 64 years old',
    u'HD': u'Number of uncertified deaths of females 45 to 64 years old',
    u'JA': u'Number of certified deaths of males over 65 years old',
    u'JB': u'Number of certified deaths of females over 65 years old',
    u'JC': u'Number of uncertified deaths of males over 65 years old',
    u'JD': u'Number of uncertified deaths of females over 65 years old',
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
