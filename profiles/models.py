# -*- coding: utf-8 -*-
from operator import or_

from django.contrib.auth.models import User
from django.db import models
from django.utils import six

from locations.models import Location


class Profile(models.Model):
    user = models.OneToOneField(User, related_name=u'profile')
    locations = models.ManyToManyField(Location, related_name=u'+')
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def filter_locations(self, queryset):
        query = (models.Q(pk__in=location.get_descendants(include_self=True))
                    for location in self.locations.all())
        query = six.functools.reduce(or_, query)

        return queryset.filter(query)
