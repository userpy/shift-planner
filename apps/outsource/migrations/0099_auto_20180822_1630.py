# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-22 13:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0098_auto_20180822_1231'),
        ('permission', '0007_convert_access_profiles')
    ]

    operations = [
        migrations.RemoveField(
            model_name='accessprofile',
            name='agency',
        ),
        migrations.RemoveField(
            model_name='accessprofile',
            name='headquater',
        ),
        migrations.RemoveField(
            model_name='accessprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='AccessProfile',
        ),
    ]
