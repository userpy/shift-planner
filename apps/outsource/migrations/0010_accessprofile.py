# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-21 08:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('outsource', '0009_auto_20180220_1703'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='outsource.Agency', verbose_name='Агентство')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Права доступа',
                'verbose_name_plural': 'Права доступа',
                'ordering': ['-id'],
            },
        ),
    ]
