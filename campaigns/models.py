# -*- coding: utf-8 -*-
from django.db import models
from django.utils.timezone import now

from common.constants import DATA_SOURCES
from locations.models import Location


class Application(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    PROGRAM_TYPES = {
        '1': 'May/June',
        '2': 'Nov/Dec',
    }

    name = models.CharField(max_length=255)
    locations = models.ManyToManyField(Location, limit_choices_to={
        u'type__name__in': [u'State', u'LGA']})
    start_date = models.DateField()
    end_date = models.DateField()
    apps = models.ManyToManyField(Application)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    source = models.CharField(
        choices=DATA_SOURCES, default=DATA_SOURCES[1][0], max_length=32)

    def __str__(self):
        return self.name

    def campaign_states(self):
        return self.locations.filter(type__name=u'State')

    def campaign_lgas(self, location):
        try:
            if self.locations.get(pk=location.pk) and location.type.name == u'State':
                return self.locations.filter(parent=location,
                    type__name=u'LGA') or location.children.all()
        except Location.DoesNotExist:
            pass

        return Location.objects.none()

    def get_related_objects(self, model_class, state, locations=None):
        try:
            if not locations:
                lgas = self.campaign_lgas(state)
                if lgas.count() == Location.objects.filter(parent=state).count():
                    return model_class.objects.filter(
                        location__code__startswith=state.code,
                        time__range=(self.start_date, self.end_date))
                else:
                    locations = state.get_descendants(include_self=True)

            return model_class.objects.filter(location__in=locations,
                time__range=(self.start_date, self.end_date))
        except Exception:
            pass

        return model_class.objects.none()

    @classmethod
    def active_campaigns(cls, location=None):
        date = now().date()
        qs = cls.objects.filter(start_date__lte=date, end_date__gte=date)

        if location is not None and isinstance(location, Location):
            return qs.filter(locations__lft__lte=location.lft,
                locations__rght__gte=location.rght)

        return qs
