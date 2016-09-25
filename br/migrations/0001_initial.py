# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '__first__'),
        ('reporters', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='BirthRegistration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('girls_below1', models.IntegerField()),
                ('girls_1to4', models.IntegerField()),
                ('girls_5to9', models.IntegerField()),
                ('girls_10to18', models.IntegerField()),
                ('boys_below1', models.IntegerField()),
                ('boys_1to4', models.IntegerField()),
                ('boys_5to9', models.IntegerField()),
                ('boys_10to18', models.IntegerField()),
                ('time', models.DateTimeField()),
                ('connection', models.ForeignKey(related_name='br_birthregistration', blank=True, to='reporters.PersistantConnection', null=True)),
                ('location', models.ForeignKey(related_name='birthregistration_records', to='locations.Location')),
                ('reporter', models.ForeignKey(related_name='br_birthregistration', blank=True, to='reporters.Reporter', null=True)),
            ],
            options={
                'permissions': (('can_view', 'Can view'),),
            },
        ),
        migrations.CreateModel(
            name='CensusResult',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField()),
                ('population', models.IntegerField()),
                ('growth_rate', models.FloatField()),
                ('under_1_rate', models.FloatField(null=True)),
                ('under_5_rate', models.FloatField(null=True)),
                ('location', models.ForeignKey(related_name='census_results', to='locations.Location')),
            ],
        ),
    ]
