# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-06 14:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0044_auto_20180306_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeeevent',
            name='dismissal_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата увольнения сотрудника'),
        ),
        migrations.AlterField(
            model_name='employeeevent',
            name='recruitment_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата приема сотрудника'),
        ),
    ]
