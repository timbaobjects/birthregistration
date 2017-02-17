from rest_framework import serializers
from locations.models import Location


class LocationSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField()

    class Meta:
        model = Location
        fields = ('id', 'name', 'type')
