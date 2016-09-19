#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.contrib import admin
from br.models import *

class BirthRegistrationAdmin(admin.ModelAdmin):
    list_display = ['location', 'reporter', 'time']
    date_hierarchy = 'time'
    search_fields = ['location__name', 'reporter__first_name', 'reporter__last_name']

admin.site.register(BirthRegistration, BirthRegistrationAdmin)