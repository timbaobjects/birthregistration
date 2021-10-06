import pandas as pd
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models

from common.constants import DATA_SOURCES
from locations.models import Location
from reporters.models import Reporter, PersistantConnection
from unicefng.querysets import SearchableLocationQuerySet


class BirthRegistrationQuerySet(SearchableLocationQuerySet):
    pass


class BirthRegistrationManager(models.Manager.from_queryset(BirthRegistrationQuerySet)):
    use_in_migrations = True


class BirthRegistration(models.Model):
    """Stores birth registration records for the different health facilities"""
    reporter = models.ForeignKey(Reporter, blank=True, null=True, related_name="br_birthregistration")
    connection = models.ForeignKey(PersistantConnection, blank=True, null=True, related_name="br_birthregistration")
    location = models.ForeignKey(Location, related_name='birthregistration_records')
    girls_below1 = models.IntegerField()
    girls_1to4 = models.IntegerField()
    girls_5to9 = models.IntegerField()
    girls_10to18 = models.IntegerField()
    boys_below1 = models.IntegerField()
    boys_1to4 = models.IntegerField()
    boys_5to9 = models.IntegerField()
    boys_10to18 = models.IntegerField()
    time = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=32, choices=DATA_SOURCES, default=DATA_SOURCES[1][0])

    objects = BirthRegistrationManager()

    def __unicode__(self):
        return "%s" % (self.pk)

    class Meta:
        permissions = (
            ("can_view", "Can view"),
        )


class CensusResult(models.Model):
    '''Stores population count'''
    location = models.ForeignKey(Location, related_name='census_results')
    year = models.IntegerField()
    population = models.IntegerField()
    growth_rate = models.FloatField()
    under_1_rate = models.FloatField(null=True)
    under_5_rate = models.FloatField(null=True)

    @staticmethod
    def get_dataframe():
        app_cache = cache

        dataframe = app_cache.get('population_estimates')
        if (type(dataframe) is not pd.DataFrame) or dataframe.empty:
            dataframe = generate_population_dataframe()
            app_cache.set('population_estimates', dataframe)

        return dataframe

    @classmethod
    def get_census_dataframe(cls, year):
        db_year = cls.objects.filter(year__lte=year).aggregate(
            max_year=models.Max(u'year')).get(u'max_year')

        qs = cls.objects.filter(year=db_year).annotate(
            loc_id=models.F(u'location__pk')).values(u'year', u'population',
            u'growth_rate', u'loc_id', u'under_1_rate', u'under_5_rate')

        dataframe = pd.DataFrame.from_records(qs).set_index(
            u'loc_id').sort_index()

        return dataframe

    @classmethod
    def get_estimate_dataframe(cls, year, month=None):
        dataframe = cls.get_census_dataframe(year)
        if month is not None:
            if month not in list(range(1, 13)):
                raise ValueError('Invalid month value')

        def _process(row):
            if month is not None:
                growth_rate = ((1 + row['growth_rate']) ** (1 / 12.0)) - 1
                exponent = (year - row['year'] - 1) + month
            else:
                growth_rate = row['growth_rate']
                exponent = (year - row['year'])

            estimate = row['population'] * (
                (1 + (growth_rate / 100)) ** exponent)
            u1_estimate = estimate * row['under_1_rate'] / 100.0
            u5_estimate = estimate * row['under_5_rate'] / 100.0

            return pd.Series(
                [estimate, u1_estimate, u5_estimate],
                index=['estimate', 'u1_estimate', 'u5_estimate'])

        return dataframe.apply(_process, axis=1)


def generate_population_dataframe():
    qs = CensusResult.objects.values(
        'location__pk', 'year', 'population',
        'growth_rate'
    )
    dataframe = pd.DataFrame(list(qs))

    return dataframe.rename(columns={
        'location__pk': 'loc_id',
    })


class Subscription(models.Model):
    subscriber = models.ForeignKey(User)
    locations = models.ManyToManyField(Location)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
