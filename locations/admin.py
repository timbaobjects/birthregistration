#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.contrib import admin
from locations.models import *

class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'type', 'parent']
    list_filter = ['type']
    search_fields = ['name', 'code']
    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'code')
        }),
        )

admin.site.register(LocationType)
admin.site.register(Location, LocationAdmin)
admin.site.register(Facility)
