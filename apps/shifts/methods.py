#
# Copyright 2018 ООО «Верме»
#
# Утилиты для работы с объектами смен, запросами аутсорсеров и т.д.

from django.db.models import Q
from django.utils import dateparse

from .models import *
from apps.outsource.models import Organization, Agency, Headquater, Config
from apps.employees.models import AgencyEmployee, JobHistory, OrgHistory, EmployeeDoc
from apps.employees.methods import check_employee_medical
from apps.outsource.methods import get_unit_list_upwards
from datetime import timedelta
from itertools import chain
import datetime


def open_outsourcing_shift(shift_id):
    """
    Возвращает объект OutsourcingShift по его ID
    """
    if not shift_id:
        return None
    try:
        shift_id = int(shift_id)
    except:
        return None
    return OutsourcingShift.objects.filter(id=shift_id).first()


def open_promo_shift(shift_id):
    """
    Возвращает объект PromoShift по его ID
    """
    if not shift_id:
        return None
    try:
        shift_id = int(shift_id)
    except:
        return None
    return PromoShift.objects.filter(id=shift_id).first()


def open_availability(avail_id):
    """
    Возвращает объект Availability по его ID
    """
    if not avail_id:
        return None
    try:
        avail_id = int(avail_id)
    except:
        return None
    return Availability.objects.filter(id=avail_id).first()


def open_outsourcing_request(request_id):
    """
    Возвращает объект OutsourcingRequest по его ID
    """
    if not request_id:
        return None
    try:
        request_id = int(request_id)
    except:
        return None
    return OutsourcingRequest.objects.filter(id=request_id).first()


def query_free_employees_for_shift(shift):
    """
    Метод возвращает список подходящщих для смены shfit сотрудников (обертка query_free_employees_for_shift_ext)
    """
    if type(shift) == OutsourcingShift:
        headquarter = shift.request.headquater
        job = shift.job
    else:
        headquarter = shift.headquarter
        job = None
    return query_free_employees_for_shift_ext(shift.agency, headquarter, shift.start, shift.end, job, [shift.id])


def query_free_employees_for_shift_ext(agency, orgunit, start, end, job=None, shift_ids=[], force_all=False):
    """
    Метод возвращает список сотрудников, подходящщих по следующим критериям на период [start, end]
    + сотрудник работает в агентстве agency
    + сотрудник авторизован для работы в orgunit(может быть как headquarter так и organization)
    + сотрудник обладает должностью job
    + у сотрудника нет других смен, исключая shift_ids
    + у сотрудника есть действующая медицинская книжка (для промоутеров)
    """
    start_date = start.date()
    end_date = end.date()
    # Определяем список занятных сотрудников агентства на выбранный период
    if agency.headquater.party == 'agency':
        query = OutsourcingShift.objects.filter(agency=agency, agency_employee__isnull=False)
    else:
        query = PromoShift.objects.filter(agency=agency, agency_employee__isnull=False)
    # Период может определяться либо точно по границам смены, либо границами дня, т.е. один и тот же сотрудник не может
    # работать на двух сменах в один день
    if isinstance(orgunit, Headquater):
        headquarter = orgunit
        organization = None
    elif isinstance(orgunit, Organization):
        headquarter = orgunit.headquater
        organization = orgunit
    else:
        headquarter = None
        organization = None
    config_value = int(Config.get(headquarter, 'max_shifts_per_day', 0))
    if config_value == 1:
        query = query.filter(start_date=start_date)
    else:
        query = query.filter(start__lt=end, end__gt=start)
    shft_employee_ids = query.exclude(state='delete').exclude(id__in=shift_ids).values_list('agency_employee_id',
                                                                                            flat=True)

    # Определяем список свободных сотрудников, которые числятся в агентстве на дату начала смены
    employee_ids = AgencyEmployee.objects.filter(Q(agency=agency, receipt__lte=start_date)
                                                 & (Q(dismissal__isnull=True) | Q(dismissal__gte=end_date)))
    if not force_all:
        employee_ids = employee_ids.exclude(id__in=shft_employee_ids)
    employee_ids = employee_ids.values_list('id', flat=True)

    # Исключаем сотрудников без необходимой должности
    if job:
        employee_ids = JobHistory.objects.filter(Q(job=job, start__lte=start_date, agency_employee_id__in=employee_ids)
                                                 & (Q(end__isnull=True) | Q(end__gte=end_date))).values_list(
            'agency_employee_id', flat=True)

    # Определяем список свободных сотрудников агентства, авторизованных для работы в компании на дату начала смены
    employee_ids = OrgHistory.objects.filter(
        Q(headquater=headquarter, agency_employee_id__in=employee_ids, start__lte=start_date)
        & (Q(end__gte=end_date) | Q(end__isnull=True))).filter(is_inactive=False)

    # Если указана конкретная организация, то фильтруем дополнительно по ней
    if organization:
        employee_ids = employee_ids.filter(Q(organization=organization) | Q(organization=organization.parent))
    employee_ids = employee_ids.values_list('agency_employee_id', flat=True)

    # Возвращаем список сотрудников в сортированном виде
    return AgencyEmployee.objects.filter(id__in=employee_ids).order_by('surname', 'firstname', 'patronymic')


def can_set_employee_to_shft(employee, shift):
    """
    Метод проверяет возможность назначения сотурдника employee на смену shift (обертка can_set_employee_to_shft_ext)
    """
    # Выходим, если сотрудник не задан или такой же как в смене
    if not employee or (shift.agency_employee and shift.agency_employee.id == employee.id):
        return True
    # Выполняем проверку условий
    if type(shift) == OutsourcingShift:
        headquarter = shift.request.headquater
        job = shift.job
    else:
        headquarter = shift.headquarter
        job = None
    return can_set_employee_to_shft_ext(employee, shift.start, shift.end, shift.agency, headquarter, job, [shift.id])


def can_set_employee_to_shft_ext(employee, start, end, agency, headquarter, job=None, shift_ids=[]):
    """
    Метод проверяет возможность назначения сотурдника employee на смену по следующим критериям:
    + сотрудник работает в агентстве agency в течение смены
    + у сотрудника нет других смен в течение смены
    + сотрудник авторизован для работы в  headquarter
    + сотрудник обладает необходимой должностью job (опциональная проверка)
    + у сотрудника есть действующая медицинская книжка на дату начала смены (для промоутеров)
    """
    start_date = start.date()
    end_date = end.date()
    # Выходим, если сотрудник не задан
    if not employee:
        return True
    # Проверяем, работает ли сотрудник в агентстве, куда отправлена смена
    if employee.agency.id != agency.id:
        return False
    if employee.receipt > start_date:
        return False
    if employee.dismissal is not None and employee.dismissal < end_date:
        return False

    # Проверяем занять ли сотрудник на других сменах
    if agency.headquater.party == 'agency':
        query = OutsourcingShift.objects.filter(agency=agency, agency_employee=employee)
    else:
        query = PromoShift.objects.filter(agency=agency, agency_employee=employee)
    # Период может определяться либо точно по границам смены, либо границами дня, т.е. один и тот же сотрудник не может
    # работать на двух сменах в один день
    config_value = int(Config.get(headquarter, 'max_shifts_per_day', 0))
    if config_value == 1:
        query = query.filter(start_date=start_date)
    else:
        query = query.filter(start__lt=end, end__gt=start)
    if query.exclude(state='delete').exclude(id__in=shift_ids).exists():
        return False

    # Проверяем, авторизован ли сотрудник для работы в магазине клиента
    if not employee.get_number_in_organization(headquarter, start.date()):
        return False

    # Проверка наличия должности у сотрудника
    if job:
        query = JobHistory.objects.filter(agency_employee=employee, job=job, start__lte=start_date)
        query = query.filter(Q(end__isnull=True) | Q(end__gte=end_date))
        if not query.exists():
            return False

    # Для промоутеров - проверяем налчие медицинской книжки
    if agency.headquater.party == 'promo' and not check_employee_medical(employee, start_date):
        return False

    # Все проверки пройдены
    return True


def make_requests_queryset(unit_headquarter=None, unit=None, date=None):
    """Формирование queryset запросов"""
    if date and not isinstance(date, datetime.date):
        date = dateparse.parse_date(date)

    """Ограничиваем по клиенту и орг. единице"""
    if unit_headquarter.party == 'agency':
        req_query_set = OutsourcingRequest.objects.filter(agency__headquater=unit_headquarter)
        if unit:
            req_query_set = req_query_set.filter(agency=unit)
    else:
        req_query_set = OutsourcingRequest.objects.filter(headquater=unit_headquarter)
        if unit:
            req_query_set = req_query_set.filter(Q(organization=unit) | Q(organization__parent=unit))

    if date:
        start = datetime.date(date.year, date.month, 1)
        end = start + timedelta(days=31)
        end = datetime.date(end.year, end.month, 1) - timedelta(days=1)
        req_query_set = req_query_set.filter(start__gte=start, end__lte=end)
        shifts_reqs_ids = OutsourcingShift.objects.filter(request__in=req_query_set,
                                                          start_date__gte=start,
                                                          start_date__lte=end). \
            order_by('request_id').distinct('request_id').values_list('request_id', flat=True)
        req_query_set = req_query_set.filter(id__in=shifts_reqs_ids)

    return req_query_set


def make_shifts_queryset(unit_headquarter=None, unit=None, date=None):
    """Формирование queryset смен"""
    if date:
        if not isinstance(date, datetime.date):
            date = dateparse.parse_date(date)
        start = datetime.date(date.year, date.month, 1)
        end = start + timedelta(days=31)
        end = datetime.date(end.year, end.month, 1) - timedelta(days=1)

    """Ограничиваем по клиенту и орг. единице"""
    if unit_headquarter.party == 'agency':
        shifts_query_set = OutsourcingShift.objects.filter(agency__headquater=unit_headquarter)
        if unit:
            shifts_query_set = shifts_query_set.filter(agency=unit)
    else:
        shifts_query_set = OutsourcingShift.objects.filter(headquater=unit_headquarter)
        if unit:
            shifts_query_set.filter(Q(request__organization=unit) | Q(request__organization__parent=unit))

    shifts_query_set = shifts_query_set.filter(state='accept')

    if date:
        shifts_query_set = shifts_query_set.filter(start_date__gte=start, start_date__lte=end)

    return shifts_query_set


# New


def get_shift_quota(shift):
    """ Получение квоты к которой относится смена """
    shift_quota = Quota.objects.filter(store=shift.organization,
                                       area=shift.store_area,
                                       promo=shift.aheadquarter). \
        filter(Q(start__lte=shift.start, end__gte=shift.end) | Q(start__lte=shift.start, end__isnull=True)). \
        order_by('-start').first()
    return shift_quota


def get_or_create_quota_info(shift):
    """ Получение связанного со сменой объекта QuotaInfo"""
    affected_quota = get_shift_quota(shift)
    if affected_quota:
        quota_info, _ = QuotaInfo.objects.get_or_create(quota=affected_quota, quota_number=shift.quota_number,
                                                        month=shift.start_date.replace(day=1))
        return quota_info


def check_availability(organization, area, agency, start, end, kind=0, avail_id=[]):
    avail = Availability.objects.filter(organization=organization, store_area=area, agency=agency, kind=kind)
    avail = avail.filter(start__lte=start, end__gte=end)
    avail = avail.exclude(id__in=avail_id).exists()
    return avail
