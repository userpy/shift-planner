# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-06 14:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0048_auto_20180306_1746'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeehistory',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='outsource.EmployeeEvent', verbose_name='Событие'),
        ),
    ]
