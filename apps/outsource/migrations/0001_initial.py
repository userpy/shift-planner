# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2018-01-25 10:16
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyEmployee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250, verbose_name='ФИО сотрудника')),
                ('number', models.CharField(max_length=250, unique=True, verbose_name='Табельный номер сотрудника')),
            ],
            options={
                'verbose_name': 'Сотрудник',
                'verbose_name_plural': 'Сотрудники',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000, verbose_name='Название функции')),
                ('code', models.CharField(max_length=1000, unique=True, verbose_name='Строковый код функции')),
            ],
            options={
                'verbose_name': 'Функция',
                'verbose_name_plural': 'Справочник функций',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='JobHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(verbose_name='Дата назначения функции')),
                ('end', models.DateField(blank=True, null=True, verbose_name='Дата окончания выполнения функции')),
                ('agency_employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.AgencyEmployee')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Job', verbose_name='Функция')),
            ],
            options={
                'verbose_name': 'История назначений',
                'verbose_name_plural': 'История назначений',
                'ordering': ['-start'],
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1000, verbose_name='Название магазина')),
                ('code', models.CharField(max_length=1000, unique=True, verbose_name='Уникальный код магазина')),
            ],
            options={
                'verbose_name': 'Магазин',
                'verbose_name_plural': 'Справочник магазинов',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='OutsourcingRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='GUID')),
                ('start', models.DateField(verbose_name='Дата начала периода')),
                ('end', models.DateField(verbose_name='Дата окончания периода')),
                ('state', models.CharField(choices=[('accepted', 'заявка получена контрагентом'), ('ready', ' заявка обработана контрагентом')], default='accepted', max_length=8, verbose_name='Статус обработки заявки')),
                ('dt_accepted', models.DateTimeField(blank=True, null=True, verbose_name='Получен')),
                ('dt_ready', models.DateTimeField(blank=True, null=True, verbose_name='Обработан')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Organization', verbose_name='Магазин')),
            ],
            options={
                'verbose_name': 'Запрос сотрудников у контрагента',
                'verbose_name_plural': 'Таблица запросов',
                'ordering': ['-start'],
            },
        ),
        migrations.CreateModel(
            name='OutsourcingShift',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='GUID')),
                ('state', models.CharField(choices=[('wait', 'ожидание ответа от контрагента'), ('accept', 'контрагент подтвердил смену'), ('reject', 'контрагент отклонил смену')], default='wait', max_length=8, verbose_name='Состояние обработки смены')),
                ('start', models.DateField(verbose_name='Дата начала смены')),
                ('end', models.DateField(verbose_name='Дата окончания смены')),
                ('worktime', models.PositiveIntegerField(blank=True, null=True, verbose_name='Рабочее время в минутах')),
                ('agency_employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.AgencyEmployee', verbose_name='Сотрудник')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Job', verbose_name='Функция')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.OutsourcingRequest')),
            ],
            options={
                'verbose_name': 'Запрашиваемая смена',
                'verbose_name_plural': 'Запрашиваемые смены',
                'ordering': ['-start'],
            },
        ),
    ]
