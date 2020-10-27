from rest_framework import serializers
from locations.models import Location


class LocationSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField()

    class Meta:
        model = Location
        fields = ('id', 'name', 'type')


class RegistrationCentreSerializer(LocationSerializer):
    lga = serializers.SerializerMethodField()
    state = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ('id', 'name', 'state', 'lga', 'type')

    def get_lga(self, centre):
        return centre.parent.name

    def get_state(self, centre):
        return centre.parent.parent.name
