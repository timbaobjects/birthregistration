# -*- coding: utf-8 -*-
from rest_framework import serializers

from br import models


class BirthReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BirthRegistration
        fields = (
            'location',
            'girls_below1',
            'girls_1to4',
            'girls_5to9',
            'girls_10to18',
            'boys_below1',
            'boys_1to4',
            'boys_5to9',
            'boys_10to18',
            'time',
        )
