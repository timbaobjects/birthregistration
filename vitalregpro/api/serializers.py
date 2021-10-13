# -*- coding: utf-8 -*-
from rest_framework import serializers

from br.models import BirthRegistration
from campaigns.models import Campaign
from common import constants
from dr.models import DeathReport, FIELD_MAP
from ipd.models import NonCompliance, Report, Shortage
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


def _death_report_data_serializer_factory():
    attributes = {
        field_name: serializers.IntegerField(
            default=0,
            help_text=description, label=field_name, min_value=0)
        for field_name, description in FIELD_MAP.items()
    }

    return type(
        'DeathReportDataSerializer', (serializers.Serializer,), attributes)


class DeathReportSerializer(serializers.ModelSerializer):
    payload = _death_report_data_serializer_factory()(
        help_text='Deaths by cause', label='Deaths', source='data')
    location = LocationCodeField(
        help_text='Location code for LGA',
        queryset=Location.objects.filter(type__name='LGA'))

    class Meta:
        model = DeathReport
        exclude = (
            'connection', 'data', 'reporter', 'source', 'created', 'updated')

    def create(self, validated_data):
        kwargs = validated_data.copy()
        kwargs.update(source=constants.DATA_SOURCES[0][0])

        return DeathReport.objects.create(**kwargs)


class CampaignSerializer(serializers.ModelSerializer):
    locations = LocationCodeField(
        many=True, queryset=Location.objects.filter(
            type__name__in=['State', 'LGA']))
    program_type = serializers.ChoiceField(
        choices=Campaign.PROGRAM_TYPES.items(), default=None)

    class Meta:
        model = Campaign
        exclude = ('apps', 'created', 'updated', 'source')
        extra_kwargs = {
            'program_type': {'write_only': True}
        }

    def create(self, validate_data):
        kwargs = validated_data.copy()
        kwargs['name'] = '{} {}'.format(
            kwargs['name'],
            Campaign.PROGRAM_TYPES.get(kwargs.pop('program_type')))
        kwargs.update(source=constants.DATA_SOURCES[0][0])

        return Campaign.objects.create(**kwargs)


class MNCHWReportSerializer(serializers.ModelSerializer):
    location = LocationCodeField(
        queryset=Location.objects.filter(
            type__name__in=['State', 'LGA', 'Ward', 'Mobilization Team']))
    
    class Meta:
        model = Report
        exclude = ('reporter', 'connection', 'created', 'updated', 'source')


class NonComplianceSerializer(serializers.ModelSerializer):
    location = LocationCodeField(queryset=Location.objects.filter(
        type__name__in=['State', 'LGA', 'Ward', 'Distribution Point']))

    class Meta:
        model = NonCompliance
        exclude = ('reporter', 'connection', 'created', 'updated', 'source')


class ShortageSerializer(serializers.ModelSerializer):
    location = LocationCodeField(queryset=Location.objects.filter(
        type__name__in=['State', 'LGA', 'Ward', 'Distribution Point']))

    class Meta:
        model = Shortage
        exclude = ('reporter', 'connection', 'created', 'updated', 'source')
