# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporters', '0002_reporter_roles'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reporter',
            name='roles',
        ),
        migrations.AddField(
            model_name='persistantconnection',
            name='reporters',
            field=models.ManyToManyField(related_name='connections_many', to='reporters.Reporter', blank=True),
        ),
    ]
