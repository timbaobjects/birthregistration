# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_mysql.models


class Migration(migrations.Migration):

    dependencies = [
        ('reporters', '__first__'),
        ('locations', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeathReport',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('data', django_mysql.models.JSONField(default=dict)),
                ('connection', models.ForeignKey(related_name='death_reports', blank=True, null=True, to='reporters.PersistantConnection')),
                ('location', models.ForeignKey(related_name='death_reports', to='locations.Location')),
                ('reporter', models.ForeignKey(related_name='death_reports', blank=True, null=True, to='reporters.Reporter')),
            ],
        ),
    ]
