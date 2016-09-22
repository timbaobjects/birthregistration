from django.core.cache import cache, get_cache, InvalidCacheBackendError
from django.db import models
import pandas as pd
from locations.models import Location
from reporters.models import Reporter, PersistantConnection
from br.managers import BirthRegistrationManager


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
        try:
            app_cache = get_cache('census_data')
        except InvalidCacheBackendError:
            app_cache = cache

        dataframe = app_cache.get('population_estimates')
        if not dataframe:
            dataframe = generate_population_dataframe()
            app_cache.set('population_estimates', dataframe)

        return dataframe


def generate_population_dataframe():
    qs = CensusResult.objects.values(
        'location__pk', 'year', 'population',
        'growth_rate'
    )
    dataframe = pd.DataFrame(list(qs))

    return dataframe.rename(columns={
        'location__pk': 'loc_id',
    })
