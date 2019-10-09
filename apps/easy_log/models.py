# coding=utf-8;

from django.db import models
from django.contrib.postgres.fields import JSONField

from apps.easy_log.settings import (
    ACTION_CHOICES, SOURCE_CHOICES, JOURNAL_STATUS, SOURCE,
    EASY_LOG, LOG_DATETIME_FORMAT
)
from apps.outsource.models import Headquater, Organization, Agency
from apps.shifts.models import OutsourcingShift, PromoShift
from apps.easy_log.signals import *


class LogManager(models.Manager):
    def get_queryset(self):
        return super(LogManager, self).get_queryset().using(
            EASY_LOG['DB_ALIAS']
        )


class LogItem(models.Model):

    objects = LogManager()

    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField(verbose_name='Дата создания')
    process_id = models.CharField(
        verbose_name='Процесс', max_length=200, null=False, blank=False)
    source = models.PositiveSmallIntegerField(
        verbose_name='Источник', default=SOURCE.TERMINAL,
        choices=SOURCE_CHOICES, db_index=True)
    source_info = models.TextField(verbose_name='Источник (инфо)',
                                   null=False, blank=False)
    action = models.PositiveSmallIntegerField(
        verbose_name='Событие', null=False, blank=False,
        choices=ACTION_CHOICES, db_index=True)
    user_id = models.IntegerField(null=True, blank=True)
    value = JSONField()
    entity_id = models.BigIntegerField(null=True, blank=True, verbose_name="идентификатор объекта")
    entity_class = models.CharField(null=True, blank=True, max_length=32, verbose_name="класс объекта")
    headquarter = models.BigIntegerField(null=True, blank=True, verbose_name="компания клиента")
    aheadquarter = models.BigIntegerField(null=True, blank=True, verbose_name="компания агентства")
    organization = models.BigIntegerField(null=True, blank=True, verbose_name="орг. единица")
    agency = models.BigIntegerField(null=True, blank=True, verbose_name="агентство")

    class Meta:
        db_table = 'easy_log'
        verbose_name = 'Журнал работы пользователей'
        verbose_name_plural = 'Журнал работы пользователей'

    def to_dict(self):
        return {
            'id': self.id,
            'created': self.created.strftime(LOG_DATETIME_FORMAT),
            'action': self.action,
            'process_id': self.process_id,
            'source': self.source,
            'source_info': self.source_info,
            'user_id': self.user_id,
            'entity_id': self.entity_id,
            'entity_class': self.entity_class,
            'value': self.value,
        }


class LogJournal(models.Model):

    objects = LogManager()

    STATUS_CHOICES = (
        (JOURNAL_STATUS.NEW, 'new'),
        (JOURNAL_STATUS.WAIT_FOR_COMMIT, 'wait for commit'),
        (JOURNAL_STATUS.FAIL, 'fail')
    )
    id = models.BigAutoField(primary_key=True)
    created = models.DateTimeField()
    process_id = models.CharField(max_length=200, null=False, blank=False)
    is_atomic = models.BooleanField(default=True)
    action = models.PositiveSmallIntegerField(null=False, blank=False,
                                              choices=ACTION_CHOICES)
    status = models.PositiveSmallIntegerField(default=1,
                                              choices=STATUS_CHOICES)
    data = JSONField()

    class Meta:
        db_table = 'easy_log_journal'
        ordering = ('-created',)
        verbose_name = 'Очередь обработки записей'
        verbose_name_plural = 'Очередь обработки записей'

    @staticmethod
    def write_to_journal(**kwargs):
        return LogJournal.objects.create(**kwargs)
