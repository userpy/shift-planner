# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-28 10:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0080_auto_20180628_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='claimrequest',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='e-mail адрес'),
        ),
        migrations.AddField(
            model_name='outsourcingrequest',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='e-mail адрес'),
        ),
        migrations.AddField(
            model_name='outsourcingrequest',
            name='user_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='ФИО пользователя'),
        ),
    ]
