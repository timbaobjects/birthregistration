# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('br', '0002_auto_20160926_0039'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('locations', models.ManyToManyField(to='locations.Location')),
                ('subscriber', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
