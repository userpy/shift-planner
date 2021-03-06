# Generated by Django 2.0.5 on 2019-03-07 08:18

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LogItem',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='Дата создания')),
                ('process_id', models.CharField(max_length=200, verbose_name='Процесс')),
                ('source', models.PositiveSmallIntegerField(choices=[(1, 'Веб-интерфейс'), (2, 'Интерфейс администратора'), (3, 'Внешняя система'), (4, 'Терминальные утилиты')], db_index=True, default=4, verbose_name='Источник')),
                ('source_info', models.TextField(verbose_name='Источник (инфо)')),
                ('action', models.PositiveSmallIntegerField(choices=[(1, 'Авторизация'), (2, 'Ошибка авторизации'), (3, 'Выход из системы'), (4, 'Создание ограничения квот'), (5, 'Редактирование ограничения квот'), (6, 'Удаление ограничения квот'), (7, 'Создание квоты'), (8, 'Редактирование квоты'), (9, 'Удаление квоты'), (10, 'Создание промо смены'), (11, 'Редактирование промо смены'), (12, 'Удаление промо смены'), (13, 'Создание аутсорс смены'), (14, 'Редактирование аутсорс смены'), (15, 'Удаление аутсорс смены')], db_index=True, verbose_name='Событие')),
                ('user_id', models.IntegerField(blank=True, null=True)),
                ('value', django.contrib.postgres.fields.jsonb.JSONField()),
                ('entity_id', models.BigIntegerField(blank=True, null=True, verbose_name='идентификатор объекта')),
                ('entity_class', models.CharField(blank=True, max_length=32, null=True, verbose_name='класс объекта')),
                ('headquarter', models.BigIntegerField(blank=True, null=True, verbose_name='компания клиента')),
                ('aheadquarter', models.BigIntegerField(blank=True, null=True, verbose_name='компания агентства')),
                ('organization', models.BigIntegerField(blank=True, null=True, verbose_name='орг. единица')),
                ('agency', models.BigIntegerField(blank=True, null=True, verbose_name='агентство')),
            ],
            options={
                'verbose_name': 'Журнал работы пользователей',
                'verbose_name_plural': 'Журнал работы пользователей',
                'db_table': 'easy_log',
            },
        ),
        migrations.CreateModel(
            name='LogJournal',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('created', models.DateTimeField()),
                ('process_id', models.CharField(max_length=200)),
                ('is_atomic', models.BooleanField(default=True)),
                ('action', models.PositiveSmallIntegerField(choices=[(1, 'Авторизация'), (2, 'Ошибка авторизации'), (3, 'Выход из системы'), (4, 'Создание ограничения квот'), (5, 'Редактирование ограничения квот'), (6, 'Удаление ограничения квот'), (7, 'Создание квоты'), (8, 'Редактирование квоты'), (9, 'Удаление квоты'), (10, 'Создание промо смены'), (11, 'Редактирование промо смены'), (12, 'Удаление промо смены'), (13, 'Создание аутсорс смены'), (14, 'Редактирование аутсорс смены'), (15, 'Удаление аутсорс смены')])),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'new'), (2, 'wait for commit'), (3, 'fail')], default=1)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
            options={
                'verbose_name': 'Очередь обработки записей',
                'verbose_name_plural': 'Очередь обработки записей',
                'db_table': 'easy_log_journal',
                'ordering': ('-created',),
            },
        ),
    ]
