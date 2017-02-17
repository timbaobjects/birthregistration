from rest_framework import generics, permissions
from rest_framework.response import Response
from locations.models import Location
from locations.serializers import LocationSerializer


# class TypedLocationListView(generics.ListAPIView):
#     '''
#     Lists all locations of a given type
#     '''
#     # permission_classes = (permissions.IsAdminUser,)
#     serializer_class = LocationSerializer

#     def get_queryset(self):
#         queryset = Location.objects.none()

#         # filter on type
#         location_type = self.request.query_params.get('type', None)
#         if location_type is not None:
#             queryset = Location.objects.filter(type__name=location_type)

#         # filter on parent id
#         parent_id = self.request.query_params.get('parent', None)
#         if parent_id:
#             queryset = queryset.filter(parent=parent_id)

#         # filter on name
#         name = self.request.query_params.get('q', None)
#         if name:
#             queryset = queryset.filter(name__istartswith=name)

#         # filter on parent name
#         parent_name = self.request.query_params.get('parent_name', None)
#         if parent_name:
#             queryset = queryset.filter(parent__name=parent_name)

#         return queryset

#     def list(self, request, *args, **kwargs):
#         self.object_list = self.filter_queryset(self.get_queryset())
#         serializer = self.get_serializer(self.object_list, many=True)

#         return Response({'locations': serializer.data})


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
