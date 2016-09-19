# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LocationType'
        db.create_table(u'locations_locationtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'locations', ['LocationType'])

        # Adding model 'Location'
        db.create_table(u'locations_location', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='locations', null=True, to=orm['locations.LocationType'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('population', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='children', null=True, to=orm['locations.Location'])),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=6, blank=True)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=6, blank=True)),
            ('lft', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True, blank=True)),
            ('rgt', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True, blank=True)),
            ('tree_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True, blank=True)),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'locations', ['Location'])

        # Adding model 'Facility'
        db.create_table(u'locations_facility', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=15)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='facilities', null=True, to=orm['locations.Location'])),
        ))
        db.send_create_signal(u'locations', ['Facility'])


    def backwards(self, orm):
        # Deleting model 'LocationType'
        db.delete_table(u'locations_locationtype')

        # Deleting model 'Location'
        db.delete_table(u'locations_location')

        # Deleting model 'Facility'
        db.delete_table(u'locations_facility')


    models = {
        u'locations.facility': {
            'Meta': {'ordering': "['name']", 'object_name': 'Facility'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'facilities'", 'null': 'True', 'to': u"orm['locations.Location']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'locations.location': {
            'Meta': {'ordering': "['name']", 'object_name': 'Location'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '6', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['locations.Location']"}),
            'population': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'rgt': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locations'", 'null': 'True', 'to': u"orm['locations.LocationType']"})
        },
        u'locations.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['locations']