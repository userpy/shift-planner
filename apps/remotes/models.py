from django.db import models
from django.contrib.postgres.fields import JSONField
import requests


class RemoteService(models.Model):
    """ Конфигурационный объект внешнего сервиса """
    PROTOCOL_CHOICES = (
        ('JSON', 'JSON'),
    )

    METHOD_CHOICES = (
        ('Sync', 'Sync'),
        ('Async', 'Async'),
    )

    name = models.CharField(verbose_name="название", max_length=128)
    description = models.CharField(verbose_name="описание", max_length=128)
    code = models.CharField(verbose_name="уникальный код", max_length=128, unique=True)
    endpoint = models.CharField(verbose_name="адрес web-службы", max_length=128)
    action = models.CharField(verbose_name="имя web-метода", max_length=128)
    oneway = models.BooleanField(verbose_name="способ взаимодействия", help_text="0 - запрос-ответ, 1 - только запрос")
    timeout = models.IntegerField(verbose_name="время ожидания ответа, сек.")
    protocol = models.CharField(
        'Протокол', max_length=4, null=False, blank=False,
        default=PROTOCOL_CHOICES[0][0], choices=PROTOCOL_CHOICES)
    login = models.CharField(
        'Логин', max_length=100, null=True, blank=True)
    password = models.CharField(
        'Пароль', max_length=100, null=True, blank=True)
    is_public = models.BooleanField('Общедоступный сервис', default=False)
    method = models.CharField(
        'Режим работы', max_length=5, null=False, blank=False,
        default=METHOD_CHOICES[0][0], choices=METHOD_CHOICES)
    params = JSONField(verbose_name="Параметры", default=dict, null=True, blank=True)

    def __str__(self):
        return self.name

    def send_sync_json_request(self, data, path, **params):
        path = f'{self.endpoint}/{self.action}/{path}/'
        data.update(params)
        req = requests.post(path, data=data, timeout=self.timeout)
        return req.json()

    @staticmethod
    def get_service(code):
        return RemoteService.objects.filter(code=code).first()

    def get_param(self, param, default):
        return self.params.get(param, default)

    def update_params(self, **kwargs):
        for (key, value) in kwargs.items():
            getattr(self, 'params')[key] = value
            self.save(update_fields=['params'])

    class Meta:
        verbose_name = 'Внешний сервис'
        verbose_name_plural = 'Внешние сервисы'
