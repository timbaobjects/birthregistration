# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import br.models


class Migration(migrations.Migration):

    dependencies = [
        ('br', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='birthregistration',
            managers=[
                ('objects', br.models.BirthRegistrationManager()),
            ],
        ),
    ]
