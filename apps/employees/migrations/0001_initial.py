# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-07-17 13:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('outsource', '0092_auto_20180717_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyEmployee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=250, verbose_name='Табельный номер')),
                ('firstname', models.CharField(max_length=250, verbose_name='Имя')),
                ('surname', models.CharField(max_length=250, verbose_name='Фамилия')),
                ('patronymic', models.CharField(blank=True, max_length=250, verbose_name='Отчество')),
                ('gender', models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский')], default='male', max_length=8, verbose_name='Пол')),
                ('date_of_birth', models.DateField(verbose_name='Дата рождения')),
                ('place_of_birth', models.CharField(blank=True, max_length=250, null=True, verbose_name='Место рождения')),
                ('receipt', models.DateField(verbose_name='Дата приема')),
                ('dismissal', models.DateField(blank=True, null=True, verbose_name='Дата увольнения')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Agency', verbose_name='Агентство')),
            ],
            options={
                'verbose_name': 'Сотрудник',
                'verbose_name_plural': 'Сотрудники',
            },
        ),
        migrations.CreateModel(
            name='AgencyHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(verbose_name='Дата назначения агентства')),
                ('end', models.DateField(blank=True, null=True, verbose_name='Дата окончания назначения агентства')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Agency', verbose_name='Агентство')),
                ('agency_employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employees.AgencyEmployee')),
            ],
            options={
                'verbose_name': 'История назначений агентств',
                'verbose_name_plural': 'История назначений агентств',
                'ordering': ['-start'],
            },
        ),
        migrations.CreateModel(
            name='EmployeeEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='GUID')),
                ('dt_created', models.DateTimeField(auto_now=True, verbose_name='Создано')),
                ('kind', models.CharField(choices=[('recruitment', 'Recruitment'), ('dismissal', 'Dismissal'), ('change', 'Change')], max_length=16, verbose_name='Вид')),
                ('recruitment_date', models.DateField(blank=True, null=True, verbose_name='Дата приема сотрудника')),
                ('dismissal_date', models.DateField(blank=True, null=True, verbose_name='Дата увольнения сотрудника')),
                ('dismissal_reason', models.CharField(blank=True, max_length=1000, verbose_name='Причина увольнения')),
                ('blacklist', models.BooleanField(default=False, verbose_name='Включен в черный список')),
                ('ext_number', models.CharField(blank=True, max_length=250, verbose_name='ТН в организации')),
                ('answer_received', models.BooleanField(default=False, verbose_name='Получен ответ на событие')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Agency', verbose_name='Агентство')),
                ('agency_employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employees.AgencyEmployee', verbose_name='Сотрудник')),
                ('headquater', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Headquater', verbose_name='Клиент')),
                ('organization', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='outsource.Organization', verbose_name='Подразделение')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Кадровое мероприятие — Внутреннее',
                'verbose_name_plural': 'Кадровые мероприятия — Внутренние',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='EmployeeHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dt_created', models.DateTimeField(auto_now=True, verbose_name='Создано')),
                ('kind', models.CharField(choices=[('accept_recruitment', 'Accept'), ('reject_recruitment', 'Reject'), ('dismissal', 'Dismissal')], max_length=20, verbose_name='Вид')),
                ('blacklist', models.BooleanField(default=False, verbose_name='Включен в черный список')),
                ('ext_number', models.CharField(blank=True, max_length=250, verbose_name='ТН в организации')),
                ('recruitment_date', models.DateField(blank=True, null=True, verbose_name='Дата приема сотрудника')),
                ('dismissal_date', models.DateField(blank=True, null=True, verbose_name='Дата увольнения сотрудника')),
                ('dismissal_reason', models.CharField(blank=True, max_length=1000, verbose_name='Причина увольнения')),
                ('reject_reason', models.CharField(blank=True, max_length=1000, verbose_name='Причина отказа')),
                ('agency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Agency', verbose_name='Агентство')),
                ('agency_employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employees.AgencyEmployee', verbose_name='Сотрудник')),
                ('event', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='employees.EmployeeEvent', verbose_name='Событие')),
                ('headquater', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Headquater', verbose_name='Клиент')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Organization', verbose_name='Подразделение')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Кадровое мероприятие — Внешнее',
                'verbose_name_plural': 'Кадровые мероприятия — Внешние',
                'ordering': ['-id'],
            },
        ),
        migrations.CreateModel(
            name='JobHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(verbose_name='С')),
                ('end', models.DateField(blank=True, null=True, verbose_name='По')),
                ('agency_employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employees.AgencyEmployee')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Job', verbose_name='Функция')),
            ],
            options={
                'verbose_name': 'История назначений функций',
                'verbose_name_plural': 'История назначений функций',
                'ordering': ['-start'],
            },
        ),
        migrations.CreateModel(
            name='OrgHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=250, verbose_name='ТН в организации')),
                ('start', models.DateField(verbose_name='Дата приема')),
                ('end', models.DateField(blank=True, null=True, verbose_name='Дата увольнения')),
                ('agency_employee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='employees.AgencyEmployee')),
                ('headquater', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Headquater', verbose_name='Клиент')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='outsource.Organization', verbose_name='Организация')),
            ],
            options={
                'verbose_name': 'История назначений организаций',
                'verbose_name_plural': 'История назначений организаций',
                'ordering': ['-start'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='orghistory',
            unique_together=set([('number', 'organization', 'start')]),
        ),
        migrations.AlterUniqueTogether(
            name='agencyemployee',
            unique_together=set([('number', 'agency')]),
        ),
    ]
