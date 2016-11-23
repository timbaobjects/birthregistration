# -*- coding: utf-8 -*-
from django.db import models
from django_mysql.models import JSONField

from locations.models import Location
from reporters.models import Reporter, PersistantConnection

FIELD_MAP = {
    u'AA': u'The number of medically certified female deaths due to childbirth and complications',
    u'AB': u'The number of uncertified female deaths due to childbirth and other complicatons',
    u'BA': u'The number of medically certified deaths of males under 1 due to fevers/typhoid',
    u'BB': u'The number of uncertified deaths of males under 1 due to fevers/typhoid',
    u'BC': u'The number of medically certified deaths of females under 1 due to fevers/typhoid',
    u'BD': u'The number of uncertified deaths of females under 1 due to fevers/typhoid',
    u'BE': u'The number of medically certified deaths of males 1-4 years old due to fevers/typhoid',
    u'BF': u'The number of uncertified deaths of males 1-4 years old due to fevers/typhoid',
    u'BG': u'The number of medically certified deaths of females 1-4 years old due to fevers/typhoid',
    u'BH': u'The number of uncertified deaths of females 1-4 years old due to fevers/typhoid',
    u'BJ': u'The number of medically certified deaths of males 5 years and older due to fevers/typhoid',
    u'BK': u'The number of uncertified deaths of males 5 years and older due to fevers/typhoid',
    u'BM': u'The number of medically certified deaths of females 5 years and older due to fevers/typhoid',
    u'BN': u'The number of uncertified deaths of females 5 years and older due to fevers/typhoid',
    u'CA': u'The number of medically certified deaths of males under 1 due to accidents and injuries',
    u'CB': u'The number of uncertified deaths of males under 1 due to accidents and injuries',
    u'CC': u'The number of medically certified deaths of females under 1 due to accidents and injuries',
    u'CD': u'The number of uncertified deaths of females under 1 due to accidents and injuries',
    u'CE': u'The number of medically certified deaths of males 1-4 years old due to accidents and injuries',
    u'CF': u'The number of uncertified deaths of males 1-4 years old due to accidents and injuries',
    u'CG': u'The number of medically certified deaths of females 1-4 years old due to accidents and injuries',
    u'CH': u'The number of uncertified deaths of females 1-4 years old due to accidents and injuries',
    u'CJ': u'The number of medically certified deaths of males 5 years and older due to accidents and injuries',
    u'CK': u'The number of uncertified deaths of males 5 years and older due to accidents and injuries',
    u'CM': u'The number of medically certified deaths of females 5 years and older due to accidents and injuries',
    u'CN': u'The number of uncertified deaths of females 5 years and older due to accidents and injuries',
    u'DA': u'The number of medically certified deaths of males under 1 due to HIV/AIDS',
    u'DB': u'The number of uncertified deaths of males under 1 due to HIV/AIDS',
    u'DC': u'The number of medically certified deaths of females under 1 due to HIV/AIDS',
    u'DD': u'The number of uncertified deaths of females under 1 due to HIV/AIDS',
    u'DE': u'The number of medically certified deaths of males 1-4 years old due to HIV/AIDS',
    u'DF': u'The number of uncertified deaths of males 1-4 years old due to HIV/AIDS',
    u'DG': u'The number of medically certified deaths of females 1-4 years old due to HIV/AIDS',
    u'DH': u'The number of uncertified deaths of females 1-4 years old due to HIV/AIDS',
    u'DJ': u'The number of medically certified deaths of males 5 years and older due to HIV/AIDS',
    u'DK': u'The number of uncertified deaths of males 5 years and older due to HIV/AIDS',
    u'DM': u'The number of medically certified deaths of females 5 years and older due to HIV/AIDS',
    u'DN': u'The number of uncertified deaths of females 5 years and older due to HIV/AIDS',
    u'EA': u'The number of medically certified deaths of males under 1 due to other ailments',
    u'EB': u'The number of uncertified deaths of males under 1 due to other ailments',
    u'EC': u'The number of medically certified deaths of females under 1 due to other ailments',
    u'ED': u'The number of uncertified deaths of females under 1 due to other ailments',
    u'EE': u'The number of medically certified deaths of males 1-4 years old due to other ailments',
    u'EF': u'The number of uncertified deaths of males 1-4 years old due to other ailments',
    u'EG': u'The number of medically certified deaths of females 1-4 years old due to other ailments',
    u'EH': u'The number of uncertified deaths of females 1-4 years old due to other ailments',
    u'EJ': u'The number of medically certified deaths of males 5 years and older due to other ailments',
    u'EK': u'The number of uncertified deaths of males 5 years and older due to other ailments',
    u'EM': u'The number of medically certified deaths of females 5 years and older due to other ailments',
    u'EN': u'The number of uncertified deaths of females 5 years and older due to other ailments',
}


class DeathReport(models.Model):
	'''
	Represents a single death record.

	Each death record contains the number of certified and uncertified
	deaths, male and female, for each cause of death, for each of the age groups below:
	- under 1y
	- 1-4y
	- 5+y
	...bringing this to a total of 50 individual data points per record (only
    females over 5 can die of childbirth and pregnancy complications)
	For this reason, we're using a JSONField (which requires MySQL 5.7+)
	'''
	location = models.ForeignKey(Location, related_name=u'death_reports')
	reporter = models.ForeignKey(Reporter, blank=True, null=True,
		related_name=u'death_reports')
	connection = models.ForeignKey(PersistantConnection, blank=True, null=True,
		related_name=u'death_reports')
	time = models.DateTimeField()
	data = JSONField()
