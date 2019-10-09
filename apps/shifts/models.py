#
# Copyright 2018 ООО «Верме»
#
# Файл моделей заявок и смен
#

from datetime import datetime, date
import uuid

from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

from apps.lib.validators import validate_dtime_15m
from apps.outsource.models import Headquater, Organization, Agency, Job, StoreArea, Quota, QuotaInfo
from apps.employees.models import AgencyEmployee
from .signals import *

REQUEST_STATE_CHOICES = (  # возможные статусы заявок (OutsourcingRequest)
    ("accepted", "Accepted"),
    ("ready", "Ready"),
)

SHIFT_STATE_CHOICES = (  # возможные состояния обработки смены (OutsourcingShift)
    ("wait", "На рассмотрении у контрагента"),
    ("accept", "Подтверждена контрагентом"),
    ("reject", "Отклонена контрагентом"),
    ("delete", "Удалена магазином"),
)


class OutsourcingRequest(models.Model):
    """Запрос сотрудников у контрагента"""
    guid = models.UUIDField(default=uuid.uuid4, verbose_name='GUID', unique=True)
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Клиент')
    organization = models.ForeignKey(Organization, blank=False, null=False, on_delete=models.PROTECT,
                                     verbose_name="Магазин")
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.PROTECT,
                               verbose_name="Агентство")
    start = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                             verbose_name="Дата начала периода")
    end = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                           verbose_name="Дата окончания периода")
    state = models.CharField(max_length=8, choices=REQUEST_STATE_CHOICES, default=REQUEST_STATE_CHOICES[0][0],
                             blank=False,
                             null=False, verbose_name="Статус обработки")
    dt_accepted = models.DateTimeField(auto_now_add=True, null=False, blank=False, verbose_name="Получен")
    dt_ready = models.DateTimeField(null=True, blank=True, verbose_name="Обработан")
    comments = models.CharField(max_length=1000, blank=True, verbose_name='Комментарий')
    email = models.EmailField(verbose_name='e-mail адрес', blank=True)
    user_name = models.CharField(max_length=255, blank=True, verbose_name='ФИО пользователя')
    reject_reason = models.CharField(max_length=1000, blank=True, verbose_name='Причина отклонения')

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Запросы на персонал"
        verbose_name = "Запрос на персонал"

    def __str__(self):
        return "{0} / {1}".format(self.organization, self.start)

    def get_request_shifts(self):
        return OutsourcingShift.objects.filter(request=self).exclude(state='delete')

    def get_request_shifts_count(self):
        return self.get_request_shifts().count()

    def get_request_shifts_duration(self):
        return self.get_request_shifts().aggregate(models.Sum('worktime'))['worktime__sum']

    def get_request_shifts_jobs(self):
        jobs = []
        for shift in self.get_request_shifts():
            if shift.job.name not in jobs:
                jobs.append(shift.job.name)
        return jobs


class OutsourcingShift(models.Model):
    """Запрашиваемая смена
    TODO:  при выборе сотрудника нужно учитывать его функции в нужный период и наоборот,
    TODO:  при выборе функции уточнять сотрудников
    """
    guid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='GUID')
    state = models.CharField(max_length=8, choices=SHIFT_STATE_CHOICES, default=SHIFT_STATE_CHOICES[0][0], blank=False,
                             null=False, verbose_name="Состояние обработки смены")
    start = models.DateTimeField(auto_now=False, auto_now_add=False, blank=False, null=False,
                                 verbose_name="Начало смены")
    end = models.DateTimeField(auto_now=False, auto_now_add=False, blank=False, null=False,
                               verbose_name="Окончание смены")
    worktime = models.PositiveIntegerField(blank=True, null=True, verbose_name="Рабочее время в минутах")
    job = models.ForeignKey(Job, blank=False, null=False, on_delete=models.PROTECT, verbose_name="Функция")
    agency_employee = models.ForeignKey(AgencyEmployee, blank=True, null=True, on_delete=models.PROTECT,
                                        verbose_name="Сотрудник")
    request = models.ForeignKey(OutsourcingRequest, blank=False, null=False, on_delete=models.PROTECT)
    dt_change = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name="Последнее изменение")
    headquater = models.ForeignKey(Headquater, blank=False, null=False, on_delete=models.PROTECT, verbose_name='Клиент')
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.PROTECT,
                               verbose_name="Агентство")
    start_date = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=True,
                                  verbose_name="День начала смены")

    @property
    def get_duration(self):
        return (self.end - self.start).total_seconds() // 60

    @property
    def get_organization_id(self):
        return self.request.organization_id

    @property
    def get_area_id(self):
        return f'{self.get_organization_id}_{self.job_id}'

    def get_employee_number_in_organization(self):
        """
        Метод возвращает табельный номер сотрудника, назначенный ему в организации клиента, если такой информации нет (например,
        на смену не назначен сотрудник, либо сотрудник не авторизован у клиента), то возвращает None.
        """
        if not self.agency_employee:
            return None
        return self.agency_employee.get_number_in_organization(self.headquater, self.start_date)

    def get_diff(self, obj):
        if obj is None:
            obj = OutsourcingShift()

        if not isinstance(obj, OutsourcingShift):
            raise Exception("OutsourcingShift.get_diff can apply only OutsourcingShift object")

        result = {}
        for attr in ['start', 'end', 'agency_employee']:
            prev_value = getattr(obj, attr)
            new_value = getattr(self, attr)
            if prev_value != new_value:
                if isinstance(prev_value, datetime):
                    prev_value = prev_value.isoformat()
                if isinstance(new_value, datetime):
                    new_value = new_value.isoformat()
                if prev_value and isinstance(prev_value, AgencyEmployee):
                    prev_value = prev_value.name
                if new_value and isinstance(new_value, AgencyEmployee):
                    new_value = new_value.name
                result.update({
                    attr: {'from': prev_value, 'to': new_value}
                })
        return result

    class Meta:
        ordering = ["-start"]
        verbose_name_plural = "Запрашиваемые смены"
        verbose_name = "Запрашиваемая смена"


class PromoShift(models.Model):
    STATE_CHOICES = (
        ("accept", "Подтверждена"),
        ("delete", "Удалена"),
    )

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Смены"
        verbose_name = "Смена"

    # ХРАНИМЫЕ ПОЛЯ
    guid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='GUID', db_index=True)
    state = models.CharField(max_length=120, blank=False, null=False, choices=STATE_CHOICES,
                             default=STATE_CHOICES[0][0], verbose_name='Состояние')
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.PROTECT,
                               verbose_name="Подразделение промоутера")
    aheadquarter = models.ForeignKey(Headquater, blank=True, null=False, on_delete=models.PROTECT,
                                     verbose_name='Компания-промоутер', related_name='aheadquarters',
                                     limit_choices_to={'party': 'promo'})
    organization = models.ForeignKey(Organization, blank=False, null=False, on_delete=models.PROTECT,
                                     verbose_name="Магазин")
    headquarter = models.ForeignKey(Headquater, blank=True, null=False, on_delete=models.PROTECT,
                                    verbose_name='Клиент', related_name='headquarters',
                                    limit_choices_to={'party': 'client'})
    store_area = models.ForeignKey(StoreArea, blank=False, null=False, on_delete=models.PROTECT,
                                   verbose_name="Зона магазина")
    quota_number = models.IntegerField(blank=False, null=False, verbose_name="Номер квоты")
    start = models.DateTimeField(auto_now=False, auto_now_add=False, blank=False, null=False,
                                 verbose_name="Начало смены", validators=[validate_dtime_15m])
    start_date = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True,
                                  verbose_name="День начала смены", db_index=True)
    end = models.DateTimeField(auto_now=False, auto_now_add=False, blank=False, null=False,
                               verbose_name="Окончание смены", validators=[validate_dtime_15m])
    duration = models.IntegerField(blank=False, null=False, verbose_name="Продолжительность", default=0)
    worktime = models.IntegerField(blank=False, null=False, verbose_name="Рабочее время", default=0)
    agency_employee = models.ForeignKey(AgencyEmployee, blank=True, null=True, on_delete=models.PROTECT,
                                        verbose_name="Сотрудник")
    dt_change = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name="Последнее изменение", db_index=True)
    year = models.PositiveIntegerField(blank=True, null=True, verbose_name='год')
    month = models.PositiveIntegerField(blank=True, null=True, verbose_name='месяц')
    day = models.PositiveIntegerField(blank=True, null=True, verbose_name='день')
    quota_info = models.ForeignKey(QuotaInfo, blank=False, null=True, on_delete=models.SET_NULL,
                                   verbose_name='Информация о квоте')

    def get_employee_number_in_organization(self):
        """
        Метод возвращает табельный номер сотрудника, назначенный ему в организации клиента, если такой информации нет (например,
        на смену не назначен сотрудник, либо сотрудник не авторизован у клиента), то возвращает None.
        """
        if not self.agency_employee:
            return None
        return self.agency_employee.get_number_in_organization(self.headquarter, self.start_date)

    def remove(self):
        """ Удаление одной смены """
        if self.state == 'accept':
            self.state = 'delete'
            self.save(update_fields=['state', 'dt_change'])
            # promo_shift_remove_signal.send(sender=self.__class__, shift=self)

    def get_diff(self, obj):
        if obj is None:
            obj = PromoShift()

        if not isinstance(obj, PromoShift):
            raise Exception("PromoShift.get_diff can apply only PromoShift object")

        result = {}
        changed_attrs = list()
        for attr in ['start', 'end', 'agency_employee']:
            prev_value = getattr(obj, attr)
            new_value = getattr(self, attr)
            if prev_value != new_value:
                if isinstance(prev_value, datetime):
                    prev_value = prev_value.isoformat()
                if isinstance(new_value, datetime):
                    new_value = new_value.isoformat()
                if prev_value and isinstance(prev_value, AgencyEmployee):
                    prev_value = prev_value.name
                if new_value and isinstance(new_value, AgencyEmployee):
                    new_value = new_value.name
                # Добавляем в массив изменных атрибутов
                changed_attrs.append(attr)
                result.update({
                    attr: {'from': prev_value, 'to': new_value}
                })
        return result

    @staticmethod
    def remove_batch(queryset):
        """ Удаление нескольких смен """

        # queryset.filter(state='accept').update(state='delete', dt_change=timezone.now())
        # То что закоментил то лучше, но по аналогии с восстановлением упрощаю, иначе понадобились бы доп пакеты
        shifts = queryset.filter(state='accept')
        for shift in shifts:
            shift.remove()
            # promo_shift_remove_signal.send(sender=PromoShift.__class__, shift=shift)

    def restore(self):
        """ Восстановление одной смены """
        if self.state == 'delete' and not self.is_intersect():
            self.state = 'accept'
            self.save(update_fields=['state', 'dt_change'])
            # promo_shift_restore_signal.send(sender=self.__class__, shift=self)

    @staticmethod
    def restore_batch(queryset):
        """ Восстановление нескольких смен """
        shifts = queryset.filter(state='delete')
        for shift in shifts:
            shift.restore()
            # promo_shift_restore_signal.send(sender=PromoShift.__class__, shift=shift)

    @staticmethod
    def find_overlay(agency, organization, store_area, quota_number, start, end, shift_ids=[]):
        """
        Метод возвращает true, если внутри заданного периода есть другие смены, и false в противном случае:
        + start, end - дата и время начала и окончания смены
        + agency - агенство
        + organization - магазин
        + store_area - зона магазине
        + quota_number - номер квоты
        + shifts_ids - массив не рассматриваемых смен
        """
        # Находим всем смены, сформированные агентством и относящиеся к заданному магазину и зоне магазина
        query = PromoShift.objects.filter(agency=agency, organization=organization, store_area=store_area)
        # Относящиеся с одной квоте и пересекающиеся с создаваемой
        query = query.filter(quota_number=quota_number, start__lt=end, end__gt=start)
        # Исключаем удаленные и заданные явно через параметры метода
        query = query.exclude(state='delete').exclude(id__in=shift_ids)
        # Возвращаем True, если наложение есть и False в протвивном случае
        return query

    def is_intersect(self):
        """  Метод возвращает true, если текущая смена пересекается с другой, и false - в противном случае """
        return PromoShift.find_overlay(self.agency, self.organization, self.store_area, self.quota_number, self.start,
                                       self.end, [self.id]).exists()

    @staticmethod
    def compress_by_quota_number(queryset, max_quota_number):
        """ Алгоритм утрамбовки смен из массива shifts - пытаемся все смены перенести на квоту до max_quota_number включительно """
        for shift in queryset:
            for quota_number in range(0, max_quota_number + 1):
                # Пропускаем, если перемещение на выбранную квоту невозможно
                shift.quota_number = quota_number
                if shift.is_intersect():
                    continue
                # Если более низкая квота свободна, то перенеосим смену на нее
                shift.save(update_fields=['quota_number', 'dt_change'])
                break

    # ВЫЧИСЛЯЕМЫЕ ПОЛЯ ДЛЯ АДМИНКИ
    def aheadquarter_agency_display(self):
        return f'{self.aheadquarter} / {self.agency}'

    aheadquarter_agency_display.short_description = 'Агентство'

    def employee_employee_number_display(self):
        if self.agency_employee:
            return f'{self.agency_employee.name} / {self.agency_employee.number}'
        else:
            return ''

    employee_employee_number_display.short_description = 'Сотрудник'

    def start_end_display(self):
        datetime_format = '%d.%m.%Y %H:%M'
        start_local = timezone.localtime(self.start)
        end_local = timezone.localtime(self.end)
        return f'{start_local.strftime(datetime_format)} - {end_local.strftime(datetime_format)}'

    start_end_display.short_description = 'С - По'

    def total_time_display(self):
        total_time_seconds = (self.end - self.start).total_seconds()
        hours = int(total_time_seconds // 3600)
        minutes = int((total_time_seconds - hours * 3600) // 60)
        return f'{hours:02}:{minutes:02}'

    total_time_display.short_description = 'Общее время'

    def worktime_display(self):
        hours = self.worktime // 60
        minutes = self.worktime % 60
        return f'{hours:02}:{minutes:02}'

    worktime_display.short_description = 'Рабочее время'

    def save(self, *args, **kwargs):
        obj = None
        if self.pk:
            obj = PromoShift.objects.filter(pk=self.pk).first()
        super(PromoShift, self).save(*args, **kwargs)
        promo_shift_change_signal.send(self.__class__, old_shift=obj, new_shift=self)


class Availability(models.Model):
    STATE_KIND = (
        (0, "Не доступен"),
        (1, "Доступен"),
    )

    class Meta:
        ordering = ["-id"]
        verbose_name_plural = "Доступности"
        verbose_name = "Доступность"

    # ХРАНИМЫЕ ПОЛЯ
    guid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='GUID')
    agency = models.ForeignKey(Agency, blank=False, null=False, on_delete=models.PROTECT,
                               verbose_name="Подразделение промоутера")
    aheadquarter = models.ForeignKey(Headquater, blank=True, null=False, on_delete=models.PROTECT,
                                     verbose_name='Компания-промоутер', related_name='avail_aheadquarters',
                                     limit_choices_to={'party': 'promo'})
    organization = models.ForeignKey(Organization, blank=False, null=False, on_delete=models.PROTECT,
                                     verbose_name="Магазин")
    headquarter = models.ForeignKey(Headquater, blank=True, null=False, on_delete=models.PROTECT,
                                    verbose_name='Клиент', related_name='avail_headquarters',
                                    limit_choices_to={'party': 'client'})
    store_area = models.ForeignKey(StoreArea, blank=False, null=False, on_delete=models.PROTECT,
                                   verbose_name="Зона магазина")
    start = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                                 verbose_name="Начало доступности")
    end = models.DateField(auto_now=False, auto_now_add=False, blank=False, null=False,
                               verbose_name="Окончание доступности")
    dt_change = models.DateTimeField(auto_now=True, null=False, blank=False, verbose_name="Последнее изменение")
    kind = models.IntegerField(blank=True, default=0, verbose_name='Тип доступности', choices=STATE_KIND)

    def get_diff(self, obj):
        if obj is None:
            obj = Availability()

        if not isinstance(obj, Availability):
            raise Exception("Availability.get_diff can apply only Availability object")

        result = {}
        changed_attrs = list()
        for attr in ['start', 'end', 'agency', 'store_area']:
            prev_value = getattr(obj, attr)
            new_value = getattr(self, attr)
            if prev_value != new_value:
                if isinstance(prev_value, date):
                    prev_value = prev_value.isoformat()
                if isinstance(new_value, date):
                    new_value = new_value.isoformat()
                if prev_value and isinstance(prev_value, Agency):
                    prev_value = prev_value.name
                if new_value and isinstance(new_value, Agency):
                    new_value = new_value.name
                if prev_value and isinstance(prev_value, StoreArea):
                    prev_value = prev_value.name
                if new_value and isinstance(new_value, StoreArea):
                    new_value = new_value.name
                # Добавляем в массив изменных атрибутов
                changed_attrs.append(attr)
                result.update({
                    attr: {'from': prev_value, 'to': new_value}
                })

        return result

    @staticmethod
    def find_overlay(agency, organization, store_area, start, end, avail_ids=[]):
        """
        Метод возвращает true, если внутри заданного периода есть другие доступности, и false в противном случае:
        + start, end - дата начала и окончания доступности
        + agency - агенство
        + organization - магазин
        + store_area - зона магазине
        + quota_number - номер квоты
        + shifts_ids - массив не рассматриваемых смен
        """
        # Находим всем смены, сформированные агентством и относящиеся к заданному магазину и зоне магазина
        query = Availability.objects.filter(agency=agency, organization=organization, store_area=store_area)
        # Пересекающиеся с создаваемой
        query = query.filter(start__lt=end, end__gt=start)
        # Исключаем заданные явно через параметры метода
        query = query.exclude(id__in=avail_ids)
        # Возвращаем True, если наложение есть и False в противном случае
        return query

    @staticmethod
    def find_shifts(agency, organization, store_area, start, end):
        """
        Метод возвращает true, если внутри заданного периода есть другие доступности, и false в противном случае:
        + start, end - дата начала и окончания доступности
        + agency - агенство
        + organization - магазин
        + store_area - зона магазине
        """
        # Находим всем смены, сформированные агентством и относящиеся к заданному магазину и зоне магазина
        query = PromoShift.objects.filter(agency=agency, organization=organization, store_area=store_area)
        # Пересекающиеся с создаваемой недоступностью
        query = query.filter(start__lt=end, end__gt=start)
        # Исключаем удаленные
        query = query.exclude(state='delete')
        return query

    def is_intersect(self):
        """  Метод возвращает true, если текущая смена пересекается с другой, и false - в противном случае """
        return Availability.find_overlay(self.agency, self.organization, self.store_area, self.start, self.end, [self.id]).exists()

    # ВЫЧИСЛЯЕМЫЕ ПОЛЯ ДЛЯ АДМИНКИ
    def aheadquarter_agency_display(self):
        return f'{self.aheadquarter} / {self.agency}'
    aheadquarter_agency_display.short_description = 'Агентство'

    def start_end_display(self):
        return f'{self.start} - {self.end}'
    start_end_display.short_description = 'С - По'


@receiver(pre_save, sender=Availability)
def on_save_availability_shift(sender, instance, **kwargs):
    # При создании новой доступности
    if not instance.pk:
        instance.headquarter = instance.organization.headquater
        instance.aheadquarter = instance.agency.headquater
    # Каждый  раз при сохранении
    # instance.start_date = instance.start
    # instance.end_date = instance.end


@receiver(pre_save, sender=PromoShift)
def on_save_promo_shift(sender, instance, **kwargs):
    # При создании новой смены
    if not instance.pk:
        instance.headquarter = instance.organization.headquater
        instance.aheadquarter = instance.agency.headquater
    # Каждый  раз при сохранении
    instance.duration = (instance.end - instance.start).total_seconds() // 60
    instance.worktime = (instance.end - instance.start).total_seconds() // 60
    instance.start_date = instance.start
    instance.year = instance.start_date.year
    instance.month = instance.start_date.month
    instance.day = instance.start_date.day
