# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-08-17 10:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('claims', '0003_auto_20180717_1607'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='claimaction',
            options={'ordering': ['name'], 'verbose_name': 'Претензия: Действие', 'verbose_name_plural': 'Справочник действий претензий'},
        ),
        migrations.AlterModelOptions(
            name='claimstatus',
            options={'ordering': ['name'], 'verbose_name': 'Претензия: Статус', 'verbose_name_plural': 'Справочник статусов претензий'},
        ),
        migrations.AlterModelOptions(
            name='claimtype',
            options={'ordering': ['-id'], 'verbose_name': 'Претензия: Тип', 'verbose_name_plural': 'Справочник типов претензий'},
        ),
    ]
