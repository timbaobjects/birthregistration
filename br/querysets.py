from django.db.models.query import QuerySet


class SearchableLocationQuerySet(QuerySet):
    def is_within(self, location):
        return self.filter(
            location__in=location.get_descendants(include_self=True))
