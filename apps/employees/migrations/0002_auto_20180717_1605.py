# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-17 13:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='agencyemployee',
            table='outsource_agencyemployee',
        ),
        migrations.AlterModelTable(
            name='agencyhistory',
            table='outsource_agencyhistory',
        ),
        migrations.AlterModelTable(
            name='employeeevent',
            table='outsource_employeeevent',
        ),
        migrations.AlterModelTable(
            name='employeehistory',
            table='outsource_employeehistory',
        ),
        migrations.AlterModelTable(
            name='jobhistory',
            table='outsource_jobhistory',
        ),
        migrations.AlterModelTable(
            name='orghistory',
            table='outsource_orghistory',
        ),
    ]
