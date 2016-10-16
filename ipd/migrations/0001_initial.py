# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporters', '__first__'),
        ('locations', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='NonCompliance',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('time', models.DateTimeField(db_index=True)),
                ('reason', models.CharField(max_length=1, choices=[('1', 'OPV Safety'), ('2', 'Child Sick'), ('3', 'Religious Belief'), ('4', 'No Felt Need'), ('5', 'Political Differences'), ('6', 'No Care Giver Consent'), ('7', 'Unhappy With Immunization Personnel'), ('8', 'Too Many Rounds'), ('9', 'Reason Not Given')], blank=True, null=True, help_text='The stated reason for non-compliance')),
                ('cases', models.PositiveIntegerField()),
                ('connection', models.ForeignKey(to='reporters.PersistantConnection', null=True, blank=True)),
                ('location', models.ForeignKey(to='locations.Location')),
                ('reporter', models.ForeignKey(to='reporters.Reporter', null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('time', models.DateTimeField(db_index=True)),
                ('immunized', models.PositiveIntegerField(blank=True, null=True, help_text='Total persons immunized')),
                ('commodity', models.CharField(max_length=10, choices=[('opv', 'Oral Polio Vaccine'), ('vita', 'Vitamin A'), ('tt', 'Tetanus Toxoid'), ('mv', 'Measles Vaccine'), ('bcg', 'Bacille Calmette-Guerin Vaccine'), ('yf', 'Yellow Fever'), ('hepb', 'Hepatitis B'), ('fe', 'Iron Folate'), ('dpt', 'Diphtheria'), ('deworm', 'Deworming'), ('sp', 'Sulphadoxie Pyrimethanol for IPT'), ('plus', 'Plus'), ('hp', 'Health Promotion'), ('fp', 'Family Planning'), ('llin', 'Long Lasting Insecticide Nets'), ('muac', 'Measurement of Upper Arm Circumference')], blank=True, null=True)),
                ('connection', models.ForeignKey(to='reporters.PersistantConnection', null=True, blank=True)),
                ('location', models.ForeignKey(to='locations.Location')),
                ('reporter', models.ForeignKey(to='reporters.Reporter', null=True, blank=True)),
            ],
            options={
                'permissions': (('can_view', 'Can view'),),
            },
        ),
        migrations.CreateModel(
            name='Shortage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('time', models.DateTimeField(db_index=True)),
                ('commodity', models.CharField(max_length=10, choices=[('opv', 'OPV'), ('vita', 'Vitamin A'), ('tt', 'Tetanus Toxoid'), ('mv', 'Measles Vaccine'), ('yf', 'Yellow Fever'), ('hepb', 'Hepatitis B'), ('folate', 'Ferrous Folate'), ('dpt', 'Diphtheria'), ('deworm', 'Deworming'), ('sp', 'Sulphadoxie Pyrimethanol for IPT'), ('plus', 'Plus')], blank=True, null=True, help_text='The commodity being reported as having a shortage')),
                ('connection', models.ForeignKey(to='reporters.PersistantConnection', null=True, blank=True)),
                ('location', models.ForeignKey(to='locations.Location')),
                ('reporter', models.ForeignKey(to='reporters.Reporter', null=True, blank=True)),
            ],
        ),
    ]
