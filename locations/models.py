#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4
import networkx as nx
from django.conf import settings
from django.core.cache import cache, caches, InvalidCacheBackendError
from django.db import connection, models
from mptt.models import MPTTModel, TreeForeignKey

from common.constants import DATA_SOURCES, DATA_SOURCE_INTERNAL


class Search(models.Lookup):
    lookup_name = 'search'

    def as_mysql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params

        return 'MATCH (%s) AGAINST (%s)' % (lhs, rhs), params


models.CharField.register_lookup(Search)
models.TextField.register_lookup(Search)


class LocationType(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Type"

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__()


class Location(MPTTModel):
    """A Location is technically a geopgraphical point (lat+long), but is often
       used to represent a large area such as a city or state. It is recursive
       via the _parent_ field, which can be used to create a hierachy (Country
       -> State -> County -> City) in combination with the _type_ field."""

    type = models.ForeignKey(LocationType, related_name="locations", blank=True, null=True)
    name = models.CharField(max_length=100, help_text="Name of location", db_index=True)
    code = models.CharField(max_length=30, unique=True)
    population = models.PositiveIntegerField(default=0, null=False, blank=False)

    parent = TreeForeignKey("Location", related_name="children", null=True, blank=True,
        help_text="The parent of this Location. Although it is not enforced, it" +\
                  "is expected that the parent will be of a different LocationType")

    latitude = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True, help_text="The physical latitude of this location")
    longitude = models.DecimalField(max_digits=8, decimal_places=6, blank=True, null=True, help_text="The physical longitude of this location")

    lft = models.PositiveIntegerField(blank=True, default=0, db_index=True)
    rgt = models.PositiveIntegerField(blank=True, default=0, db_index=True)
    tree_id = models.PositiveIntegerField(blank=True, default=0, db_index=True)
    level = models.PositiveIntegerField(blank=True, default=0, db_index=True)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    source = models.CharField(
        max_length=32, choices=DATA_SOURCES, default=DATA_SOURCE_INTERNAL)
    vrp_id = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        if hasattr(self, 'type') and self.type:
            return "%s %s" % (self.name, self.type.name)
        else:
            return self.name

    def __str__(self):
        return self.__unicode__()

    class Meta:
        ordering = ['name']

    class MPTTMeta:
        left_attr = 'lft'
        right_attr = 'rgt'
        tree_id_attr = 'tree_id'
        level_attr = 'level'
        order_insertion_by = ['code']

    # TODO: how can we port the Location.contacts and Location.one_contact
    #       methods, now that the locations app has been split from reporters?
    #       even if they can import one another, they can't know if they're
    #       both running at parse time, and can't monkey-patch later.
    def one_contact(self, role, display=False):
        return ""

    @classmethod
    def get_by_code(cls, code):
        try:
            return cls.objects.get(code=code)
        except cls.DoesNotExist:
            return None

    @classmethod
    def _get_locations_graph(cls, reverse=False):
        if reverse:
            if not hasattr(cls, '_reversed_locations_graph'):
                cls._reversed_locations_graph = get_locations_graph(reverse)
            return cls._reversed_locations_graph
        else:
            if not hasattr(cls, '_locations_graph'):
                cls._locations_graph = get_locations_graph()
            return cls._locations_graph

    @classmethod
    def _subnodes(cls, node, type):
        graph = cls._get_locations_graph()
        descendant_ids = nx.topological_sort(graph, graph.subgraph(nx.dfs_tree(graph, node['id']).nodes()).nodes())

        if type:
            return (graph.node[i] for i in descendant_ids if graph.node[i]['type'] == type)
        else:
            return (graph.node[i] for i in descendant_ids)

    def contacts(self, role=None):
        return Location.objects.get(pk=2)

    def ancestors(self, include_self=False):
        """Returns all of the parent locations of this location,
           optionally including itself in the output. This is
           very inefficient, so consider caching the output.

           This is currently used as a convenience method as recent
           versions of django-mptt handle this adequately."""

        return self.get_ancestors(include_self=include_self)

    def descendants(self, include_self=False):
        """Returns all of the locations which are descended from this location,
           optionally including itself in the output. This is very inefficient
           (it recurses once for EACH), so consider caching the output.

           New improvements, please see doc for ancestors method."""

        return self.get_descendants(include_self=include_self)

    @property
    def node(self):
        graph = self._get_locations_graph()
        return graph.node[self.pk]

    def nx_descendants(self, include_self=False):
        graph = self._get_locations_graph()
        descendant_ids = nx.topological_sort(graph, graph.subgraph(nx.dfs_tree(graph, self.id).nodes()).nodes())
        if include_self:
            return [graph.node[id] for id in descendant_ids]
        else:
            return [graph.node[id] for id in descendant_ids if id != self.id]

    def nx_ancestors(self, include_self=False):
        reversed_graph = self._get_locations_graph(reverse=True)
        ancestor_ids = nx.topological_sort(reversed_graph, reversed_graph.subgraph(nx.dfs_tree(reversed_graph, self.id).nodes()).nodes())
        if include_self:
            return [reversed_graph.node[id] for id in ancestor_ids]
        else:
            return [reversed_graph.node[id] for id in ancestor_ids if id != self.id]

    def nx_children(self):
        reversed_graph = self._get_locations_graph()
        children_ids = reversed_graph.successors(self.id)
        return [reversed_graph.node[id] for id in children_ids]

    def _get_annual_population_estimate(self, year):
        result = None

        if self.type.name not in ('Country', 'State', 'LGA'):
            return result

        try:
            result = self.census_results.filter(location=self, year__lte=year).latest('year')
        except Exception:
            return result
        diff = year - result.year
        projection = result.population * ((1 + (result.growth_rate / 100.0)) ** diff)

        return int(round(projection))

    def center_count(self):
        return self.get_descendants(include_self=True).filter(type__name='RC').count()

    def get_annual_population_growth_estimate(self, year):
        # previous_projection = self._get_annual_population_estimate(year - 1)
        # current_projection = self._get_annual_population_estimate(year)

        # return int(round(current_projection - previous_projection))

        return self._get_annual_population_estimate(year)

    def get_monthly_population_growth_estimate(self, year):
        # previous_projection = self._get_annual_population_estimate(year - 1)
        # current_projection = self._get_annual_population_estimate(year)

        # return int(round((current_projection - previous_projection) / 12.0))

        return int(round(self._get_annual_population_estimate(year) / 12.0))

    def get_stock(self):
        from supply.models import Stock
        try:
            stock = Stock.objects.get(location=self)
        except Stock.DoesNotExist:
            stock = None

        return stock


def get_locations_graph(reverse=False):
    try:
        app_cache = caches['graphs']
    except InvalidCacheBackendError:
        app_cache = cache

    graph = app_cache.get('reversed_locations_graph') if reverse else app_cache.get('locations_graph')
    if not graph:
        if reverse:
            graph = generate_locations_graph().reverse()
            app_cache.set('reversed_locations_graph', graph, settings.LOCATIONS_GRAPH_MAXAGE)
        else:
            graph = generate_locations_graph()
            app_cache.set('locations_graph', graph, settings.LOCATIONS_GRAPH_MAXAGE)
    return graph


def generate_locations_graph():
    location_qs = Location.objects.order_by('level', 'name').values(
        'pk', 'name', 'parent__pk', 'type__name', 'active')
    graph = nx.DiGraph()

    for loc_info in location_qs.filter(parent__pk=None):
        graph.add_node(
            loc_info['pk'],
            name=loc_info['name'],
            id=loc_info['pk'],
            type=loc_info['type__name'],
            active=loc_info['active'])

    for loc_info in location_qs.exclude(parent__pk=None):
        graph.add_node(
            loc_info['pk'],
            name=loc_info['name'],
            id=loc_info['pk'],
            type=loc_info['type__name'],
            active=loc_info['active'])
        graph.add_edge(loc_info['parent__pk'], loc_info['pk'])

    return graph


class Facility(models.Model):
    '''A facility can be anything from a cold store to a health facility'''
    name = models.CharField(max_length=100, help_text='The common name given to the facility')
    code = models.CharField(max_length=15, help_text='code used to represent this facility')
    location = models.ForeignKey(Location, blank=True, null=True, related_name="facilities")

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name
