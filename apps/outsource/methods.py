#
# Copyright 2018 ООО «Верме»
#
# Сервисные методы для работы с данными, получаемыми со страницы

from .models import *
from apps.easy_log.shortcuts import log_promo_shift_del
from apps.shifts.models import PromoShift
from django.utils import dateparse, timezone
import datetime
from datetime import timedelta

def open_orgunit(unit_code):
    """
    Возвращает объект компании и орг. еденицы по ее коду ID_Модель
    """
    # Открываем объект выбранной орг. единицы
    selected = open_unit(unit_code)
    if not selected:
        return None, None
    elif type(selected) == Headquater:
        return selected, None
    else:
        return selected.headquater, selected

def open_unit(unit_code):
    """
    Возвращает объект орг. единицы по ее коду ID_Модель
    """
    if not unit_code:
        return None
    splitted = unit_code.split('_')
    if len(splitted) != 2:
        return None
    # Определяем ID и название модели
    unit_id = splitted[0]
    unit_class = splitted[1]

    # Определяем объект орг. структуры
    if unit_class == 'headquater':
        return open_headquarter(unit_id)
    elif unit_class == 'agency':
        return open_agency(unit_id)
    elif unit_class == 'organization':
        return open_organization(unit_id)
    else:
        return None

def open_headquarter(headquarter_id):
    """
    Возвращает объект Headquater по его ID
    """
    if not headquarter_id:
        return None
    try:
        headquarter_id = int(headquarter_id)
    except:
        return None
    return Headquater.objects.filter(id=headquarter_id).first()

def open_headquarter_by_code(code):
    """
    Возвращает объект Headquater по его ID
    """
    if not code:
        return None
    return Headquater.objects.filter(code=code).first()

def open_agency(agency_id):
    """
    Возвращает объект Agency по его ID
    """
    if not agency_id:
        return None
    try:
        agency_id = int(agency_id)
    except:
        return None
    return Agency.objects.filter(id=agency_id).first()

def open_agency_by_code(code, headquarter):
    """
    Возвращает объект Agency по его коду и головной компании
    """
    return Agency.objects.filter(code=code).first()

def open_organization(organization_id):
    """
    Возвращает объект Organization по его ID
    """
    if not organization_id:
        return None
    try:
        organization_id = int(organization_id)
    except:
        return None
    return Organization.objects.filter(id=organization_id).first()

def open_organization_by_code(code, headquarter = None):
    """
    Возвращает объект Organization по его коду и головной компании
    """
    if not code:
        return None
    if not headquarter:
        return Organization.objects.filter(code=code).first()
    else:
        return Organization.objects.filter(headquater=headquarter, code=code).first()

def open_storearea(store_area_id):
    """
    Возвращает объект StoreArea по его ID
    """
    if not store_area_id:
        return None
    try:
        store_area_id = int(store_area_id)
    except:
        return None
    return StoreArea.objects.filter(id=store_area_id).first()

def open_quota(quota_id):
    """
    Возвращает объект Quota по его ID
    """
    if not quota_id:
        return None
    try:
        quota_id = int(quota_id)
    except:
        return None
    return Quota.objects.filter(id=quota_id).first()

def open_quota(quota_id):
    """
    Возвращает объект Quota по его ID
    """
    if not quota_id:
        return None
    try:
        quota_id = int(quota_id)
    except:
        return None
    return Quota.objects.filter(id=quota_id).first()

def open_quota_volume(quota_volume_id):
    """
    Возвращает объект QuotaVolume по его ID
    """
    if not quota_volume_id:
        return None
    try:
        quota_volume_id = int(quota_volume_id)
    except:
        return None
    return QuotaVolume.objects.filter(id=quota_volume_id).first()

def open_job(job_id):
    """
    Возвращает объект Job по его ID
    """
    if not job_id:
        return None
    try:
        job_id = int(job_id)
    except:
        return None
    return Job.objects.filter(id=job_id).first()

def get_unit_list_upwards(units):
    """
    Сервисный метод, принимает на вход один объект или массив объектов Agency или Organization и возвращает список,
    идентификаторов включающий переданный объект, а также список вышестоящих объектов
    """
    # Результирующий массив идентификаторов страниц
    unit_ids = []

    # Внутренний метод
    def add_unit_with_parents(one_unit, unit_ids):
        unit = one_unit
        # Добавляем в список саму страницу и родительскую по отношению к ней
        while unit and not unit.id in unit_ids:
            unit_ids.append(unit.id)
            unit = unit.parent
    
    # Передан один объект
    if type(units) == Organization or type(units) == Agency:
        add_unit_with_parents(units, unit_ids)
    # Передан массив объектов
    else:
        for one_unit in units:
            add_unit_with_parents(one_unit, unit_ids)
    # Возвращаем сформированный массив
    return unit_ids

def get_unit_list_downwards(headquarter, unit, recursive = False):
    """
    Возвращаем массив ID объектов орг. структуры, относящихся к компании headquarter, 
    начиная и включая орг. единицы unit. Параметр recursive определяет глубинку поиска:
    False - только нижестоящий уровень, True - все нижние уровни
    """
    units_ids = []
    # Структурная еденица не указана, следовательно берем все подразделения компании
    if not unit:
        if headquarter.party == 'client':
            units_ids = Organization.objects.filter(headquater=headquarter).values_list('id', flat=True)
        else:
            units_ids = Agency.objects.filter(headquater=headquarter).values_list('id', flat=True)
        units_ids = list(units_ids)
    # Структурная еденица указан, соледовательно возвращае ее и нижестоящие
    else:
        # Добавляем нижестоящие TODO - позже реализовать рекурсию
        if recursive:
            if headquarter.party == 'client':
                units_ids = Organization.objects.filter(headquater=headquarter, parent=unit).values_list('id', flat=True)
            else:
                units_ids = Agency.objects.filter(headquater=headquarter, parent=unit).values_list('id', flat=True)
        units_ids = list(units_ids)
        # Добаляем саму орг. единицу
        units_ids.append(unit.id)
    # Возвращаем список орг. единиц
    return units_ids

def clients_by_agency(agency):
    """
    Метод возвращает QuerySet со списком объектов Headquater вида 'cleint', с которыми может работать агентство agency
    """
    headquarters_ids = OrgLink.objects.filter(agency=agency, headquater__isnull=False).values_list('headquater_id', flat=True)
    return Headquater.objects.filter(id__in=headquarters_ids)

def cities_by_agency(agency, headquarter):
    """
    Метод возвращает QuerySet со списком объектов Organization типа 'city', с которыми разрешено работать агентству agency в клиенте headquarter
    """
    headquarters_ids = OrgLink.objects.filter(agency=agency, headquater=headquarter).values_list('organization_id', flat=True)
    return Organization.objects.filter(id__in=headquarters_ids).exclude(kind='store')

def agency_ids_by_aheadquarter(aheadquarter):
    """ Возвращает id агентств входящих в компанию агентства """
    return Agency.objects.filter(headquater=aheadquarter).values_list('id', flat=True)

def active_quota(store, area, promo, start):
    """
    Поиск квоты по магазину, зоне и промо-агентству и дате
    """
    return Quota.objects.filter(store=store, area=area, promo=promo, start__lte=start).order_by('-start').first()

def similar_quota(store, area, promo, start):
    """
    Поиск дубликата квоты по магазину, зоне, промо-агентству и дате начала
    """
    return Quota.objects.filter(store=store, area=area, promo=promo, start=start).first()

def active_quota_volume(store, area, start):
    """
    Поиск ограничения квоты по магазину, зоне и дате начала
    """
    return QuotaVolume.objects.filter(store=store, area=area, start=start).first()

def get_quota_related_shifts(quota, value_from=None, value_to=None):
    """ Метод возвращает связанные с квотой quota смены """
    # Запускаем поиск
    queryset = PromoShift.objects.filter(headquarter=quota.headquarter, organization=quota.store)
    queryset = queryset.filter(store_area=quota.area, aheadquarter=quota.promo, start__gte=quota.start)
    # Проверяем нет ли других квот, которые влияют на смену, если у квоты не заполнена дата окончания
    if not quota.end:
        other_affected_quotas = Quota.objects.filter(headquarter=quota.headquarter,
                                                     store=quota.store,
                                                     area=quota.area,
                                                     promo=quota.promo,
                                                     start__gte=quota.start). \
            exclude(id=quota.id).order_by('start').first()
        if other_affected_quotas:
            queryset = queryset.filter(end__lt=other_affected_quotas.start)
    else:
        queryset = queryset.filter(end__lte=quota.end)
    # Номер квоты в смене начинается с 0, поэтому вычитаем 1
    if value_from:
        queryset = queryset.filter(quota_number__gte=(value_from-1))
    if value_to:
        queryset = queryset.filter(quota_number__lte=(value_to - 1))
    return queryset.exclude(state='delete')


def get_quota_volume_related_quotas(quota_volume):
    """ Метод возвращает связанные с ограничение квоты квоты """
    # Запускаем поиск
    queryset = Quota.objects.filter(store=quota_volume.store, area=quota_volume.area)
    queryset = queryset.filter(Q(start=quota_volume.start, end=quota_volume.end) |
                               Q(start=quota_volume.start, end__isnull=True))
    # Проверяем нет ли других ограничений, которые влияют на квоту, если у ограничения не заполнена дата окончания
    if not quota_volume.end:
        other_affected_quotas_volume = QuotaVolume.objects.filter(start__gte=quota_volume.start). \
            exclude(id=quota_volume.id).order_by('start').first()
        if other_affected_quotas_volume:
            queryset = queryset.filter(end__lt=other_affected_quotas_volume.start)
    return queryset

def remove_quota_related_shifts(quota, user_id=None, value_from=None, value_to=None):
    """ Метод удаляет связанные с квотой смены """
    shifts = get_quota_related_shifts(quota, value_from, value_to)
    log_handler = log_promo_shift_del
    for shift in shifts:
        shift.quota_info = None
        log_handler(user_id=user_id,
                    entity_id=shift.id,
                    headquarter=shift.headquarter_id,
                    promo=shift.aheadquarter_id,
                    organization=shift.organization_id,
                    agency=shift.agency_id,
                    start=shift.start,
                    end=shift.end,
                    source_info=None,
                    diff={},
                    store_area=shift.store_area.name
                    )
    PromoShift.remove_batch(shifts)
    return shifts


def remove_quota_volume_related_quota(quota_volume):
    """ Метод удаляет связанные с ограничением квоты квоты """
    quotas = get_quota_volume_related_quotas(quota_volume)
    Quota.remove_batch(quotas)

def remove_quota(quota, user_id=None):
    """ Удаление одной квоты """
    if quota:
        # Удаляем связанные со сменой квоты
        quota_shifts = remove_quota_related_shifts(quota, user_id)
        # Удаляем связанные объекты QuotaInfo
        QuotaInfo.objects.filter(quota=quota).delete()
        # Удаляем саму квоту
        quota.delete()
        # Перепривязываем смены к другой QuotaInfo
        #from apps.shifts.methods import get_or_create_quota_info
        #for shift in quota_shifts:
        #    shift.quota_info = get_or_create_quota_info(shift)
        #    shift.save()


def remove_quota_volume(quota_volume):
    """ Удаление одного ограничения квоты """
    if quota_volume:
        # Удаляем связанные с ограничение квоты
        #remove_quota_volume_related_quotas(quota_volume)
        # Удаляем само ограничение квоты
        quota_volume.delete()

def remove_quotas(quotas):
    """ Удаление нескольких квот """
    for quota in quotas:
        remove_quota(quota)

def set_quota_value(quota, new_value):
    """ Метод присваивает новое значение квоты """
    # Выходим, если значение не изменилось
    #if quota.value == new_value:
    #    return
    # В случае снижения квоты пытаемся провести утрамбовку связанных с квотой смен, если после утрамбовки смены
    # все же выходят за пределы новой квоты, то мы их удаляем
    if new_value:
        new_value = int(new_value)
        # Определяем список смен, выходящих за новый объем квоты
        shifts = get_quota_related_shifts(quota, new_value + 1)
        # Запускаем для них алгоритм утрамбовки (-1, т.к. нумерация в сменах начинается с 0)
        PromoShift.compress_by_quota_number(shifts, new_value - 1)
        # Удаляем смены, которые не удалось перенести
        remove_quota_related_shifts(quota, None, new_value + 1, 0)
    # Сохраняем новое значение квоты
    #quota.value = new_value
    #quota.save()

@receiver(pre_save, sender=Quota)
def on_save_quota(sender, instance, **kwargs):
    """ Назначение компании-клиента """
    instance.headquarter = instance.store.headquater
    if instance:
        set_quota_value(instance, instance.value_total)

def make_quotas_queryset(unit_headquarter=None, unit=None, date=None):
    """Формирование queryset квот"""
    if date and not isinstance(date, datetime.date):
        date = dateparse.parse_date(date)
    if not date:
        date = timezone.now().date()

    """Ограничиваем по клиенту и орг. единице"""
    if unit_headquarter.party == 'promo':
        quotas_query_set = Quota.objects.filter(promo=unit_headquarter)
    else:
        quotas_query_set = Quota.objects.filter(headquarter=unit_headquarter)
        if unit:
            quotas_query_set = quotas_query_set.filter(Q(store=unit) | Q(store__parent=unit))

    if date:
        start = datetime.date(date.year, date.month, 1)
        end = start + timedelta(days=31)
        end = datetime.date(end.year, end.month, 1) - timedelta(days=1)
        # Получаем квоты, которые действуют на текущий месяц
        quotas_query_set = quotas_query_set.filter(
            Q(start__lte=start, end__isnull=True) | Q(start__lte=start, end__gte=end))

    return quotas_query_set

def make_quotas_volume_queryset(unit_headquarter=None, unit=None, date=None):
    """Формирование queryset ограничений квот"""
    if date and not isinstance(date, datetime.date):
        date = dateparse.parse_date(date)
    if not date:
        date = timezone.now().date()

    """Ограничиваем по клиенту и орг. единице"""
    quotas_volume_query_set = QuotaVolume.objects.filter(store__headquater=unit_headquarter)
    if unit:
        quotas_volume_query_set = quotas_volume_query_set.filter(Q(store=unit) | Q(store__parent=unit))

    if date:
        start = datetime.date(date.year, date.month, 1)
        end = start + timedelta(days=31)
        end = datetime.date(end.year, end.month, 1) - timedelta(days=1)
        # Получаем ограничения квот, которые действуют на текущий месяц
        quotas_volume_query_set = quotas_volume_query_set.filter(
            Q(start__lte=start, end__isnull=True) | Q(start__lte=start, end__gte=end))

    return quotas_volume_query_set
