# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-04-12 12:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0059_auto_20180410_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='agency',
            name='jobs',
            field=models.ManyToManyField(to='outsource.Job', verbose_name='Функции'),
        ),
    ]
