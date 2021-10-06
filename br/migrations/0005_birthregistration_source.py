# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-10-05 12:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('br', '0004_auto_20190903_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='birthregistration',
            name='source',
            field=models.CharField(choices=[(b'external', b'External'), (b'internal', b'Internal')], default=b'internal', max_length=32),
        ),
    ]
