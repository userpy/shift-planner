# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-28 08:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0069_auto_20180524_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='claimattach',
            name='mime',
            field=models.CharField(max_length=255, null=True, verbose_name='MIME-тип'),
        ),
        migrations.AddField(
            model_name='claimattach',
            name='size',
            field=models.IntegerField(null=True, verbose_name='Размер'),
        ),
    ]
