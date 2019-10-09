# coding=utf-8;

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth.models import User


class NotifyItem(models.Model):

    STATUS_PENDING = 0
    STATUS_PROCESS = 1
    STATUS_DONE = 2
    STATUS_SKIP = 3
    STATUS_FAIL = 4

    STATUS_CHOICES = (
        (STATUS_PENDING, 'В ожидании'),
        (STATUS_PROCESS, 'Идет отправка'),
        (STATUS_DONE, 'Отправлено'),
        (STATUS_SKIP, 'Пропуск'),
        (STATUS_FAIL, 'Ошибка'),
    )

    SEND_METHOD_SMS = 'sms'
    SEND_METHOD_EMAIL = 'email'
    SEND_METHOD_BY_CHOICE = 'by_choice'

    SEND_METHOD_CHOICES = (
        (SEND_METHOD_SMS, 'SMS'),
        (SEND_METHOD_EMAIL, 'E-mail'),
        (SEND_METHOD_BY_CHOICE, 'По выбору сотрудника'),
    )

    template_slug = models.SlugField('Template slug')
    params = JSONField(verbose_name='Параметры', help_text='Параметры, передаваемые в сообщение', default={})
    created = models.DateTimeField(auto_now=True)
    status = models.SmallIntegerField('Статус', choices=STATUS_CHOICES, default=STATUS_PENDING)
    send_method = models.CharField(max_length=10, choices=SEND_METHOD_CHOICES, default=SEND_METHOD_EMAIL)
    error_text = models.TextField(verbose_name='Ошибка отправления', max_length=500, default='', blank=True)
    email = models.EmailField(verbose_name='e-mail адрес', blank=True)
    full_name = models.CharField(max_length=255, blank=True, verbose_name='ФИО пользователя')

    # TODO: по мере развития здесь будут добавляться поля с типами связок и пр.
    class Meta:
        db_table = 'notification_items'
        verbose_name = 'Очередь оповещения'
        verbose_name_plural = 'Очередь оповещений'
