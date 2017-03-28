# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.db import models

from locations.models import Location


class Profile(models.Model):
    user = models.OneToOneField(User, related_name=u'profile')
    locations = models.ManyToManyField(Location, related_name=u'+')
