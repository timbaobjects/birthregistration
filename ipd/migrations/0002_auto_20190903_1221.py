# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-09-03 11:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipd', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='noncompliance',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='noncompliance',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='report',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='report',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='shortage',
            name='created',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='shortage',
            name='updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='report',
            name='commodity',
            field=models.CharField(blank=True, choices=[(b'opv', b'Oral Polio Vaccine'), (b'vita', b'Vitamin A'), (b'tt', b'Tetanus Toxoid'), (b'mv', b'Measles Vaccine'), (b'bcg', b'Bacille Calmette-Guerin Vaccine'), (b'yf', b'Yellow Fever'), (b'hepb', b'Hepatitis B'), (b'fe', b'Iron Folate'), (b'dpt', b'Diphtheria'), (b'deworm', b'Deworming'), (b'sp', b'Sulphadoxie Pyrimethanol for IPT'), (b'plus', b'Plus'), (b'hp', b'Health Promotion'), (b'fp', b'Family Planning'), (b'llin', b'Long Lasting Insecticide Nets'), (b'muac', b'Measurement of Upper Arm Circumference'), (b'penta', b'Pentavalent Vaccine')], max_length=10, null=True),
        ),
    ]
