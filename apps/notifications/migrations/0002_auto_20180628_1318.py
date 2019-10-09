# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-06-28 10:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifyitem',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='e-mail адрес'),
        ),
        migrations.AddField(
            model_name='notifyitem',
            name='full_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='ФИО пользователя'),
        ),
        migrations.AlterField(
            model_name='notifyitem',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
