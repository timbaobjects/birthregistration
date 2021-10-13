# -*- coding: utf-8 -*-
from django.db import models

from common.constants import DATA_SOURCES
from locations.models import Location
from reporters.models import PersistantConnection, Reporter


class Report(models.Model):
    IM_COMMODITIES = (
        ('opv', 'Oral Polio Vaccine'),
        ('vita', 'Vitamin A'),
        ('tt', 'Tetanus Toxoid'),
        ('mv', 'Measles Vaccine'),
        ('bcg', 'Bacille Calmette-Guerin Vaccine'),
        ('yf', 'Yellow Fever'),
        ('hepb', 'Hepatitis B'),
        ('fe', 'Iron Folate'),
        ('dpt', 'Diphtheria'),
        ('deworm', 'Deworming'),
        ('sp', 'Sulphadoxie Pyrimethanol for IPT'),
        ('plus', 'Plus'),
        ('hp', 'Health Promotion'),
        ('fp', 'Family Planning'),
        ('llin', 'Long Lasting Insecticide Nets'),
        ('muac', 'Measurement of Upper Arm Circumference'),
        ('penta', 'Pentavalent Vaccine'),
    )

    reporter = models.ForeignKey(Reporter, blank=True, null=True)
    connection = models.ForeignKey(PersistantConnection, blank=True, null=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField(db_index=True)
    immunized = models.PositiveIntegerField(blank=True, null=True,
        help_text=u'Total persons immunized')
    commodity = models.CharField(choices=IM_COMMODITIES, max_length=10,
        blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    source = models.CharField(
        choices=DATA_SOURCES, default=DATA_SOURCES[1][0], max_length=32)

    class Meta:
        permissions = (
            (u'can_view', u'Can view'),
        )

    def __str__(self):
        return u'{} ({}) => {}, {}'.format(self.location, self.reporter,
            self.commodity, self.immunized)


class NonCompliance(models.Model):
    NC_REASONS = (
        ('1', 'OPV Safety'),
        ('2', 'Child Sick'),
        ('3', 'Religious Belief'),
        ('4', 'No Felt Need'),
        ('5', 'Political Differences'),
        ('6', 'No Care Giver Consent'),
        ('7', 'Unhappy With Immunization Personnel'),
        ('8', 'Too Many Rounds'),
        ('9', 'Reason Not Given'),
    )

    reporter = models.ForeignKey(Reporter, blank=True, null=True)
    connection = models.ForeignKey(PersistantConnection, blank=True, null=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField(db_index=True)
    reason = models.CharField(choices=NC_REASONS, max_length=1, blank=True,
        null=True, help_text=u'The stated reason for non-compliance')
    cases = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    source = models.CharField(
        choices=DATA_SOURCES, default=DATA_SOURCES[1][0], max_length=32)


class Shortage(models.Model):
    SHORTAGE_COMMODITIES = (
        ('opv', 'OPV'),
        ('vita', 'Vitamin A'),
        ('tt', 'Tetanus Toxoid'),
        ('mv', 'Measles Vaccine'),
        ('yf', 'Yellow Fever'),
        ('hepb', 'Hepatitis B'),
        ('folate', 'Ferrous Folate'),
        ('dpt', 'Diphtheria'),
        ('deworm', 'Deworming'),
        ('sp', 'Sulphadoxie Pyrimethanol for IPT'),
        ('plus', 'Plus'),
    )

    reporter = models.ForeignKey(Reporter, null=True, blank=True)
    connection = models.ForeignKey(PersistantConnection, null=True, blank=True)
    location = models.ForeignKey(Location)
    time = models.DateTimeField(db_index=True)
    commodity = models.CharField(blank=True, null=True, max_length=10,
        choices=SHORTAGE_COMMODITIES,
        help_text=u'The commodity being reported as having a shortage')
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    source = models.CharField(
        choices=DATA_SOURCES, default=DATA_SOURCES[1][0], max_length=32)

    def __str__(self):
        return u'{} ({}) => {}'.format(self.reporter, self.location,
            self.commodity)
