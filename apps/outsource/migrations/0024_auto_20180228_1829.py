# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-28 15:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0023_auto_20180228_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agencyemployee',
            name='number',
            field=models.CharField(max_length=250, verbose_name='Табельный номер сотрудника'),
        ),
        migrations.AlterUniqueTogether(
            name='agencyemployee',
            unique_together=set([('number', 'agency')]),
        ),
    ]
