# -*- coding: utf-8 -*-
from rest_framework import serializers

from br.models import BirthRegistration
from common import constants
from locations.models import Location, LocationType


class LocationCodeField(serializers.RelatedField):
    def to_internal_value(self, data):
        location = Location.get_by_code(data)

        return location

    def to_representation(self, value):
        return value.code


class BirthReportSerializer(serializers.ModelSerializer):
    location = LocationCodeField(
        queryset=Location.objects.filter(type__name='RC'),
        help_text='Location code for registration centre.')

    class Meta:
        model = BirthRegistration
        exclude = ('reporter', 'connection', 'created', 'updated', 'source')

    def create(self, validated_data):
        kwargs = validated_data.copy()
        kwargs.update(source=constants.DATA_SOURCES[0][0])

        return BirthRegistration.objects.create(**kwargs)


class LocationParentField(serializers.RelatedField):
    def to_internal_value(self, data):
        return Location.objects.get(code=data)

    def to_representation(self, value):
        if value.type.name.lower() == 'zone':
            return value.parent.code

        return value.code


class LocationSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField()
    parent = LocationParentField(queryset=Location.objects.all())

    class Meta:
        model = Location
        fields = ('name', 'type', 'code', 'parent')
        read_only_fields = ('code',)

    def create(self, validated_data):
        lga = validated_data.get('parent')
        rc_type = LocationType.objects.get(name__iexact='RC')
        last_rc_code = lga.children.filter(
            type__name='RC'
        ).order_by('-code').first().code

        try:
            next_rc_code = str(int(last_rc_code) + 1).zfill(9)
        except ValueError:
            raise serializers.ValidationError('The centre could not be added due to an error')

        return Location.objects.create(
            code=next_rc_code, type=rc_type, source=constants.DATA_SOURCES[0][0],
            **validated_data)

    def validate_parent(self, parent):
        if parent.type.name.lower() != 'lga':
            raise serializers.ValidationError('Can only create centres in LGAs')

        return parent
