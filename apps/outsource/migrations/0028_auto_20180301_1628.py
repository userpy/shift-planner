# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-01 13:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0027_auto_20180301_1555'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='EmployeeHisory',
            new_name='EmployeeHistory',
        ),
    ]
