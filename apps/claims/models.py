#
# Copyright 2018 ООО «Верме»
#
# Файл моделей претензий
#

from django.db import models
from django.utils import timezone
from apps.outsource.models import Headquater, Organization, Agency, PARTY_CHOICES
import uuid


def user_directory_path(instance, filename):
    n = timezone.now()

    if isinstance(instance, ClaimAttach):
        if instance.claim:
            return 'claims/{year}/{month}/{day}/claim_{id}/{file}'.format(id=instance.claim.id, year=n.year,
                                                                          month=n.month, day=n.day, file=filename)
        if instance.message:
            return 'claims/{year}/{month}/{day}/claim_{id}/{file}'.format(id=instance.message.claim.id, year=n.year,
                                                                          month=n.month, day=n.day, file=filename)
    if isinstance(instance, Document):
        if instance.headquater:
            return 'documents/{head_code}/{year}/{month}/{day}/{file}'.format(head_code=instance.headquater.code, year=n.year,
                                                                              month=n.month, day=n.day, file=filename)


# CLAIM_PARTY_CHOICES = (
#     ("agency", "Агентство"),
#     ("client", "Клиент"),
# )


class ClaimStatus(models.Model):
    """Статусы претензий"""
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name='Код')
    sort_key = models.PositiveIntegerField(default=1, verbose_name='индекс сортировки')

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Справочник статусов претензий"
        verbose_name = "Претензия: Статус"

    def __str__(self):
        return "{0} / {1}".format(self.name, self.code)


class ClaimAction(models.Model):
    """Действия по претензии"""
    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name='Название')
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name='Код')
    sort_key = models.PositiveIntegerField(default=1, verbose_name='индекс сортировки')
    need_comment = models.BooleanField(default=False, null=False, verbose_name='требуется комментарий')

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Справочник действий претензий"
        verbose_name = "Претензия: Действие"

    def __str__(self):
        return "{0} / {1}".format(self.name, self.code)


class ClaimType(models.Model):
    """Тип претензии"""
    name = models.CharField(max_length=250, blank=False, null=False, verbose_name='Название')
    code = models.CharField(max_length=250, blank=False, null=False, unique=True, verbose_name='Код')
    sort_key = models.IntegerField(blank=False, null=False, verbose_name='Порядок вывода')

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Справочник типов претензий"
        verbose_name = "Претензия: Тип"

    def __str__(self):
        return "{0} / {1}".format(self.code, self.name)


class ClaimRequest(models.Model):
    """Претензия"""
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Клиент')
    organization = models.ForeignKey(Organization, blank=False, null=False, on_delete=models.PROTECT,
                                     verbose_name="Магазин")
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.PROTECT, verbose_name="Агентство")
    text = models.TextField(blank=False, null=False, verbose_name="Текст претензии")
    user_name = models.CharField(max_length=255, blank=True, verbose_name='ФИО пользователя')
    #number = models.IntegerField(blank=False, verbose_name='Номер')
    claim_type = models.ForeignKey(ClaimType, blank=False, null=False, on_delete=models.PROTECT,
                                   verbose_name='Тип')
    dt_created = models.DateTimeField(auto_now_add=True, null=False, blank=False,  verbose_name="Создана")
    dt_updated = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name="Обновлена")
    dt_status_changed = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Изменен статус")
    guid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='GUID')
    email = models.EmailField(verbose_name='e-mail адрес', blank=True)
    status = models.ForeignKey(ClaimStatus, blank=True, null=True, on_delete=models.PROTECT, verbose_name="Статус")

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Претензии"
        verbose_name = "Претензия"

    @property
    def number(self):
        return f"{self.headquater.prefix}{self.id}"

    def __str__(self):
        return "{0} / {1}".format(self.id, self.headquater)


class ClaimMessage(models.Model):
    """Сообщение"""
    claim = models.ForeignKey(ClaimRequest, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Претензия')
    party = models.CharField(max_length=8, choices=PARTY_CHOICES, blank=False, null=False, verbose_name='Тип')
    text = models.TextField(blank=False, null=False, verbose_name="Текст сообщения")
    user_name = models.CharField(max_length=255, blank=True, verbose_name='ФИО пользователя')
    dt_created = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name="Создан")

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Сообщения"
        verbose_name = "Сообщение"

    def __str__(self):
        return "{0} / {1}".format(self.id, self.claim)


class ClaimHistory(models.Model):
    """История согласований"""
    dt_created = models.DateTimeField(auto_now_add=True, null=False, blank=False,  verbose_name="обновлено")
    party = models.CharField(max_length=8, choices=PARTY_CHOICES, blank=False, null=False, verbose_name='Сторона')
    user_name = models.CharField(max_length=255, blank=True, verbose_name='ФИО пользователя')
    comment = models.TextField(blank=True, null=True, verbose_name="Комментаний")
    claim = models.ForeignKey(ClaimRequest, blank=False, null=False, on_delete=models.CASCADE, verbose_name='Претензия')
    state_from = models.ForeignKey(ClaimStatus, models.CASCADE, verbose_name='предыдущее состояние', related_name='+')
    state_to = models.ForeignKey(ClaimStatus, models.CASCADE, verbose_name='текущее состояние', related_name='+')

    class Meta:
        ordering = ["-dt_created"]
        verbose_name_plural = "Истории согласований"
        verbose_name = "История согласований"

    def __str__(self):
        return "{0} / {1} / {2} / {3}".format(self.claim, self.state_from, self.state_to, self.dt_created)


class FileBase(models.Model):
    """Файлы"""
    filename = models.CharField(max_length=255, blank=False, null=False, verbose_name='Название файла')
    size = models.IntegerField(null=True, verbose_name='Размер')
    mime = models.CharField(max_length=255, null=True, verbose_name='MIME-тип')
    attachment = models.FileField(upload_to=user_directory_path, verbose_name='Путь')
    dt_created = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name="Создан")

    class Meta:
        abstract = True


class Document(FileBase):
    """Документы"""
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Клиент')
    description = models.TextField(blank=False, null=False, verbose_name="Описание")

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Документы"
        verbose_name = "Документ"

    def __str__(self):
        return "{0} / {1}".format(self.filename, self.headquater)


class ClaimAttach(FileBase):
    """Прикрепленный файл"""
    claim = models.ForeignKey(ClaimRequest, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Претензия')
    message = models.ForeignKey(ClaimMessage, null=True, blank=True, on_delete=models.PROTECT, verbose_name='Сообщение')

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Файлы"
        verbose_name = "Файл"

    def __str__(self):
        return "{0} / {1}".format(self.filename, self.claim)
