# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-05-23 11:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0065_auto_20180523_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='claimattach',
            name='message',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='outsource.ClaimMessage', verbose_name='Сообщение'),
        ),
    ]
