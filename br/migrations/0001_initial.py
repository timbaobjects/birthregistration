# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'BirthRegistration'
        db.create_table('br_birthregistration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reporter', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='br_birthregistration', null=True, to=orm['reporters.Reporter'])),
            ('connection', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='br_birthregistration', null=True, to=orm['reporters.PersistantConnection'])),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(related_name='birthregistration_records', to=orm['locations.Location'])),
            ('girls_under5', self.gf('django.db.models.fields.IntegerField')()),
            ('girls_over5', self.gf('django.db.models.fields.IntegerField')()),
            ('boys_under5', self.gf('django.db.models.fields.IntegerField')()),
            ('boys_over5', self.gf('django.db.models.fields.IntegerField')()),
            ('time', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('br', ['BirthRegistration'])


    def backwards(self, orm):
        
        # Deleting model 'BirthRegistration'
        db.delete_table('br_birthregistration')


    models = {
        'br.birthregistration': {
            'Meta': {'object_name': 'BirthRegistration'},
            'boys_over5': ('django.db.models.fields.IntegerField', [], {}),
            'boys_under5': ('django.db.models.fields.IntegerField', [], {}),
            'connection': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'br_birthregistration'", 'null': 'True', 'to': "orm['reporters.PersistantConnection']"}),
            'girls_over5': ('django.db.models.fields.IntegerField', [], {}),
            'girls_under5': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'birthregistration_records'", 'to': "orm['locations.Location']"}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'br_birthregistration'", 'null': 'True', 'to': "orm['reporters.Reporter']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'locations.location': {
            'Meta': {'ordering': "['name']", 'object_name': 'Location'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '6', 'blank': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'lft': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '6', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'population': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'rgt': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'tree_id': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'db_index': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'locations'", 'null': 'True', 'to': "orm['locations.LocationType']"})
        },
        'locations.locationtype': {
            'Meta': {'object_name': 'LocationType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'patterns.pattern': {
            'Meta': {'object_name': 'Pattern'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'regex': ('django.db.models.fields.CharField', [], {'max_length': '160'})
        },
        'reporters.persistantbackend': {
            'Meta': {'object_name': 'PersistantBackend'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        'reporters.persistantconnection': {
            'Meta': {'unique_together': "(('backend', 'identity'),)", 'object_name': 'PersistantConnection'},
            'backend': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'connections'", 'to': "orm['reporters.PersistantBackend']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identity': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'last_seen': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'connections'", 'null': 'True', 'to': "orm['reporters.Reporter']"})
        },
        'reporters.reporter': {
            'Meta': {'ordering': "['last_name', 'first_name']", 'object_name': 'Reporter'},
            'alias': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'reporters'", 'blank': 'True', 'to': "orm['reporters.ReporterGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reporters'", 'null': 'True', 'to': "orm['locations.Location']"}),
            'registered_self': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'role': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'reporters'", 'null': 'True', 'to': "orm['reporters.Role']"})
        },
        'reporters.reportergroup': {
            'Meta': {'object_name': 'ReporterGroup'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'children'", 'null': 'True', 'to': "orm['reporters.ReporterGroup']"}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'reporters.role': {
            'Meta': {'object_name': 'Role'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '160'}),
            'patterns': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['patterns.Pattern']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['br']
