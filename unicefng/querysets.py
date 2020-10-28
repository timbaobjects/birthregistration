from django.db.models.query import Q, QuerySet

from profiles.models import Profile


class SearchableLocationQuerySet(QuerySet):
    def is_within(self, location):
        return self.filter(
            location__in=location.get_descendants(include_self=True))

    def filter_supervised_locations(self, user):
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            return self

        query = Q()
        for location in profile.locations.all():
            query = query | Q(location__in=location.get_descendants(
                include_self=True))

        return self.filter(query)
