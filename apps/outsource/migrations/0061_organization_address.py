# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-17 10:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0060_agency_jobs'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='address',
            field=models.CharField(blank=True, max_length=1000, verbose_name='Адрес'),
        ),
    ]
