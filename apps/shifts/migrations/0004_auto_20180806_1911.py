# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-06 16:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0003_auto_20180717_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='outsourcingshift',
            name='state',
            field=models.CharField(choices=[('wait', 'На рассмотрении у контрагента'), ('accept', 'Подтверждена контрагентом'), ('reject', 'Отклонена контрагентом'), ('delete', 'Удалена магазином')], default='wait', max_length=8, verbose_name='Состояние обработки смены'),
        ),
    ]
