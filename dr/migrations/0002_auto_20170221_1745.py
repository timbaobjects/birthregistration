# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('dr', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deathreport',
            name='time',
        ),
        migrations.AddField(
            model_name='deathreport',
            name='date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
