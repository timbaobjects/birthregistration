# -*- coding: utf-8 -*-
from django.contrib import admin

from profiles.forms import ProfileAdminForm
from profiles.models import Profile


class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm
    list_display = (u'user',)
    search_fields = (u'user__username',)


admin.site.register(Profile, ProfileAdmin)
