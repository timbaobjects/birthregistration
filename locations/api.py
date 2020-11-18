from rest_framework import generics
from locations.models import Location
from locations.serializers import LocationSerializer


class LocationItemView(generics.RetrieveAPIView):
    '''
    Retrieves a single location
    '''
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class LocationListView(generics.ListAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

    def get_queryset(self):
        queryset = super(LocationListView, self).get_queryset()

        # filter on prefix (for name-based lookups)
        prefix = self.request.query_params.get(u'q', None)
        if prefix:
            queryset = queryset.filter(name__istartswith=prefix)

        return queryset


class TypedLocationListView(LocationListView):
    def get_queryset(self):
        queryset = super(TypedLocationListView, self).get_queryset()

        # type is required
        # this works without case sensitivity on MySQL
        # TODO: implement explicit case-insensitivity
        type_names = self.request.query_params.get(u'type')
        if not type_names:
            return queryset.none()

        types = type_names.split(u',')
        queryset = queryset.filter(type__name__in=types)

        # filter on parent id
        parent_id = self.request.query_params.get(u'parent')
        if parent_id:
            queryset = queryset.filter(parent=parent_id)

        return queryset
