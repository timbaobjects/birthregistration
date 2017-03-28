from django.contrib.auth.models import User
from django.core.cache import cache, get_cache, InvalidCacheBackendError
from django.db import models
import pandas as pd
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
        if (type(dataframe) is not pd.DataFrame) or dataframe.empty:
            dataframe = generate_population_dataframe()
            app_cache.set('population_estimates', dataframe)

        return dataframe

    @staticmethod
    def get_census_dataframe(year):
        db_year = CensusResult.objects.filter(year__lte=year).aggregate(
            max_year=models.Max(u'year')).get(u'max_year')

        qs = CensusResult.objects.filter(year=db_year).annotate(
            loc_id=models.F(u'location__pk')).values(u'year', u'population',
            u'growth_rate', u'loc_id', u'under_1_rate', u'under_5_rate')

        dataframe = pd.DataFrame.from_records(qs).set_index(
            u'loc_id').sort_index()

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


class Subscription(models.Model):
    subscriber = models.ForeignKey(User)
    locations = models.ManyToManyField(Location)
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
