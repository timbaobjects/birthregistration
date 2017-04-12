# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '__first__'),
        ('patterns', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersistantBackend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.CharField(unique=True, max_length=30)),
                ('title', models.CharField(max_length=30)),
            ],
            options={
                'verbose_name': 'Backend',
            },
        ),
        migrations.CreateModel(
            name='PersistantConnection',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identity', models.CharField(max_length=30)),
                ('last_seen', models.DateTimeField(null=True, blank=True)),
                ('backend', models.ForeignKey(related_name='connections', to='reporters.PersistantBackend')),
            ],
            options={
                'verbose_name': 'Connection',
            },
        ),
        migrations.CreateModel(
            name='Reporter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alias', models.CharField(unique=True, max_length=20)),
                ('first_name', models.CharField(max_length=30, blank=True)),
                ('last_name', models.CharField(max_length=30, blank=True)),
                ('language', models.CharField(max_length=10, blank=True)),
                ('registered_self', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['last_name', 'first_name'],
                'permissions': (('can_view', 'Can view'),),
            },
        ),
        migrations.CreateModel(
            name='ReporterGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=30)),
                ('description', models.TextField(blank=True)),
                ('parent', models.ForeignKey(related_name='children', blank=True, to='reporters.ReporterGroup', null=True)),
            ],
            options={
                'verbose_name': 'Group',
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=160)),
                ('code', models.CharField(help_text=b'Abbreviation', max_length=20, null=True, blank=True)),
                ('patterns', models.ManyToManyField(to='patterns.Pattern', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='reporter',
            name='groups',
            field=models.ManyToManyField(related_name='reporters', to='reporters.ReporterGroup', blank=True),
        ),
        migrations.AddField(
            model_name='reporter',
            name='location',
            field=models.ForeignKey(related_name='reporters', blank=True, to='locations.Location', null=True),
        ),
        migrations.AddField(
            model_name='reporter',
            name='role',
            field=models.ForeignKey(related_name='reporters', blank=True, to='reporters.Role', null=True),
        ),
        migrations.AddField(
            model_name='persistantconnection',
            name='reporter',
            field=models.ForeignKey(related_name='connections', blank=True, to='reporters.Reporter', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='persistantconnection',
            unique_together=set([('backend', 'identity')]),
        ),
    ]
