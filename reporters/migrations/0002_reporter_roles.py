# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporters', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reporter',
            name='roles',
            field=models.ManyToManyField(related_name='_reporter_roles_+', to='reporters.Role', blank=True),
        ),
    ]
