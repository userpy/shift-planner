# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-06 15:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0049_auto_20180306_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orghistory',
            name='number',
            field=models.CharField(max_length=250, verbose_name='ТН в организации'),
        ),
        migrations.AlterUniqueTogether(
            name='orghistory',
            unique_together=set([('number', 'organization')]),
        ),
    ]
