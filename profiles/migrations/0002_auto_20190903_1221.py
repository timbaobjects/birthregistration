# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-03 11:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
    ]