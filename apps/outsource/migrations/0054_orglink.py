# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-03-20 10:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion



class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0053_set_headquater'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrgLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agency', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='outsource.Agency', verbose_name='Агентство')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Organization', verbose_name='Организация')),
            ],
            options={
                'verbose_name': 'Организация агентства',
                'verbose_name_plural': 'Организации агентства',
                'ordering': ['-id'],
            },
        ),
    ]
