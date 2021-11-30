# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-11-23 13:32
from __future__ import unicode_literals

import django.core.validators
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
        migrations.AlterField(
            model_name='birthregistration',
            name='boys_10to18',
            field=models.IntegerField(help_text=b'The number of boys registered between 10 and 18 years old', validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Boys (10)'),
        ),
        migrations.AlterField(
            model_name='birthregistration',
            name='boys_1to4',
            field=models.IntegerField(help_text=b'The number of boys registered between 1 and 4 years old', validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Boys (1 to 4)'),
        ),
        migrations.AlterField(
            model_name='birthregistration',
            name='boys_5to9',
            field=models.IntegerField(help_text=b'The number of boys registered between 5 and 9 years old', validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Boys (5 to 9)'),
        ),
        migrations.AlterField(
            model_name='birthregistration',
            name='boys_below1',
            field=models.IntegerField(help_text=b'The number of boys registered under 1 year old', validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Boys (under 1)'),
        ),
        migrations.AlterField(
            model_name='birthregistration',
            name='girls_10to18',
            field=models.IntegerField(help_text=b'The number of girls registered between 10 and 18 years old', validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Girls (10)'),
        ),
        migrations.AlterField(
            model_name='birthregistration',
            name='girls_1to4',
            field=models.IntegerField(help_text=b'The number of girls registered between 1 and 4 years old', validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Girls (1 to 4)'),
        ),
        migrations.AlterField(
            model_name='birthregistration',
            name='girls_5to9',
            field=models.IntegerField(help_text=b'The number of girls registered between 5 and 9 years old', validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Girls (5 to 9)'),
        ),
        migrations.AlterField(
            model_name='birthregistration',
            name='girls_below1',
            field=models.IntegerField(help_text=b'The number of girls registered under 1 year old', validators=[django.core.validators.MinValueValidator(0)], verbose_name=b'Girls (under 1)'),
        ),
        migrations.AlterField(
            model_name='birthregistration',
            name='time',
            field=models.DateTimeField(help_text=b'The UTC timestamp for the record creation'),
        ),
    ]
