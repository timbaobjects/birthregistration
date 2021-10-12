# -*- coding: utf-8 -*-
from datetime import date
from django.db import models
from django_mysql.models import JSONField

from common.constants import DATA_SOURCES
from dr.utils import pick, values
from locations.models import Location
from reporters.models import Reporter, PersistantConnection
from unicefng.querysets import SearchableLocationQuerySet

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

class Groups(object):
    male = [u'BA', u'BB', u'BE', u'BF', u'BJ', u'BK', u'CA', u'CB', u'CE', u'CF', u'CJ', u'CK', u'DA', u'DB', u'DE', u'DF', u'DJ', u'DK', u'EA', u'EB', u'EE', u'EF', u'EJ', u'EK']
    female = [u'AA', u'AB', u'BC', u'BD', u'BG', u'BH', u'BM', u'BN', u'CC', u'CD', u'CG', u'CH', u'CM', u'CN', u'DC', u'DD', u'DG', u'DH', u'DM', u'DN', u'EC', u'ED', u'EG', u'EH', u'EM', u'EN']
    certified = [u'AA', u'BA', u'BC', u'BE', u'BG', u'BJ', u'BM', u'CA', u'CC', u'CE', u'CG', u'CJ', u'CM', u'DA', u'DC', u'DE', u'DG', u'DJ', u'DM', u'EA', u'EC', u'EE', u'EG', u'EJ', u'EM']
    uncertified = [u'AB', u'BB', u'BD', u'BF', u'BH', u'BK', u'BN', u'CB', u'CD', u'CF', u'CH', u'CK', u'CN', u'DB', u'DD', u'DF', u'DH', u'DK', u'DN', u'EB', u'ED', u'EF', u'EH', u'EK', u'EN']
    childbirth = [u'AA', u'AB']
    fevers = [u'BA', u'BB', u'BC', u'BD', u'BE', u'BF', u'BG', u'BH', u'BJ', u'BK', u'BM', u'BN']
    accidents = [u'CA', u'CB', u'CC', u'CD', u'CE', u'CF', u'CG', u'CH', u'CJ', u'CK', u'CM', u'CN']
    hiv = [u'DA', u'DB', u'DC', u'DD', u'DE', u'DF', u'DG', u'DH', u'DJ', u'DK', u'DM', u'DN']
    other = [u'EA', u'EB', u'EC', u'ED', u'EE', u'EF', u'EG', u'EH', u'EJ', u'EK', u'EM', u'EN']
    underOne = [u'BA', u'BB', u'BC', u'BD', u'CA', u'CB', u'CC', u'CD', u'DA', u'DB', u'DC', u'DD', u'EA', u'EB', u'EC', u'ED']
    oneToFour = [u'BE', u'BF', u'BG', u'BH', u'CE', u'CF', u'CG', u'CH', u'DE', u'DF', u'DG', u'DH', u'EE', u'EF', u'EG', u'EH']
    fiveAndOlder = [u'AA', u'AB', u'BJ', u'BK', u'BM', u'BN', u'CJ', u'CK', u'CM', u'CN', u'DJ', u'DK', u'DM', u'DN', u'EJ', u'EK', u'EM', u'EN']


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
    date = models.DateField(default=date.today)
    data = JSONField()
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=32, choices=DATA_SOURCES, default=DATA_SOURCES[1][0])

    # manager
    objects = SearchableLocationQuerySet.as_manager()

    def male(self):
        return sum(values(pick(Groups.male, self.data)))

    def female(self):
        return sum(values(pick(Groups.female, self.data)))

    def certified(self):
        return sum(values(pick(Groups.certified, self.data)))

    def uncertified(self):
        return sum(values(pick(Groups.uncertified, self.data)))

    def childbirth(self):
        return sum(values(pick(Groups.childbirth, self.data)))

    def fevers(self):
        return sum(values(pick(Groups.fevers, self.data)))

    def accidents(self):
        return sum(values(pick(Groups.accidents, self.data)))

    def hiv(self):
        return sum(values(pick(Groups.hiv, self.data)))

    def other(self):
        return sum(values(pick(Groups.other, self.data)))

    def underOne(self):
        return sum(values(pick(Groups.underOne, self.data)))

    def oneToFour(self):
        return sum(values(pick(Groups.oneToFour, self.data)))

    def fiveAndOlder(self):
        return sum(values(pick(Groups.fiveAndOlder, self.data)))
