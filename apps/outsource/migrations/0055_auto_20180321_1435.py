# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-21 11:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0054_orglink'),
    ]

    operations = [
        migrations.AddField(
            model_name='orglink',
            name='headquater',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='outsource.Headquater', verbose_name='Клиент'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orglink',
            name='agency',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.PROTECT, to='outsource.Agency', verbose_name='Агентство'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='orglink',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='outsource.Organization', verbose_name='Организация'),
        ),
    ]
