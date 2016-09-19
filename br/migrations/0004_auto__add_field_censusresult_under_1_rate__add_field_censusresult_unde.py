# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'CensusResult.under_1_rate'
        db.add_column(u'br_censusresult', 'under_1_rate',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)

        # Adding field 'CensusResult.under_5_rate'
        db.add_column(u'br_censusresult', 'under_5_rate',
                      self.gf('django.db.models.fields.FloatField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'CensusResult.under_1_rate'
        db.delete_column(u'br_censusresult', 'under_1_rate')

        # Deleting field 'CensusResult.under_5_rate'
        db.delete_column(u'br_censusresult', 'under_5_rate')


    models = {
        u'br.birthregistration': {
            'Meta': {'object_name': 'BirthRegistration'},
            'boys_10to18': ('django.db.models.fields.IntegerField', [], {}),
            'boys_1to4': ('django.db.models.fields.IntegerField', [], {}),
            'boys_5to9': ('django.db.models.fields.IntegerField', [], {}),
            'boys_below1': ('django.db.models.fields.IntegerField', [], {}),
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'br_birthregistration'", 'null': 'True', 'to': u"orm['reporters.PersistantConnection']"}),
            'girls_10to18': ('django.db.models.fields.IntegerField', [], {}),
            'girls_1to4': ('django.db.models.fields.IntegerField', [], {}),
            'girls_5to9': ('django.db.models.fields.IntegerField', [], {}),
            'girls_below1': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'birthregistration_records'", 'to': u"orm['locations.Location']"}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'br_birthregistration'", 'null': 'True', 'to': u"orm['reporters.Reporter']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'br.censusresult': {
            'Meta': {'object_name': 'CensusResult'},
            'growth_rate': ('django.db.models.fields.FloatField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'census_results'", 'to': u"orm['locations.Location']"}),
            'population': ('django.db.models.fields.IntegerField', [], {}),
            'under_1_rate': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'under_5_rate': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {})
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
        },
        u'patterns.pattern': {
            'Meta': {'object_name': 'Pattern'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'regex': ('django.db.models.fields.CharField', [], {'max_length': '160'})
        },
        u'reporters.persistantbackend': {
            'Meta': {'object_name': 'PersistantBackend'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'reporters.persistantconnection': {
            'Meta': {'unique_together': "(('backend', 'identity'),)", 'object_name': 'PersistantConnection'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'connections'", 'to': u"orm['reporters.PersistantBackend']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'connections'", 'null': 'True', 'to': u"orm['reporters.Reporter']"})
        },
        u'reporters.reporter': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Reporter'},
            'alias': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'reporters'", 'blank': 'True', 'to': u"orm['reporters.ReporterGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reporters'", 'null': 'True', 'to': u"orm['locations.Location']"}),
            'registered_self': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reporters'", 'null': 'True', 'to': u"orm['reporters.Role']"})
        },
        u'reporters.reportergroup': {
            'Meta': {'object_name': 'ReporterGroup'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': u"orm['reporters.ReporterGroup']"}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'reporters.role': {
            'Meta': {'object_name': 'Role'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'patterns': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['patterns.Pattern']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['br']