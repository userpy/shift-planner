# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-01-26 10:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0003_auto_20180126_1504'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='outsourcingrequest',
            options={'ordering': ['-id'], 'verbose_name': 'Запрос сотрудников у контрагента', 'verbose_name_plural': 'Таблица запросов'},
        ),
        migrations.AlterField(
            model_name='outsourcingshift',
            name='end',
            field=models.DateTimeField(verbose_name='Окончание смены'),
        ),
        migrations.AlterField(
            model_name='outsourcingshift',
            name='start',
            field=models.DateTimeField(verbose_name='Начало смены'),
        ),
    ]
