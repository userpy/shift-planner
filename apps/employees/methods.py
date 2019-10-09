#
# Copyright 2018 ООО «Верме»
#
# Утилиты для работы с объектами сотрудников

import datetime
from django.db.models import Q, Max
from .models import *
from apps.lib.methods import make_error_response
from apps.outsource.models import Headquater, Config
from apps.outsource.methods import cities_by_agency, agency_ids_by_aheadquarter
from apps.permission.methods import check_struct_access_to_page
from apps.shifts.models import OutsourcingShift, PromoShift
from apps.remotes.models import RemoteService
from datetime import timedelta
from wfm.settings import TIME_ZONE
import pytz
from django.utils.timezone import make_aware
from itertools import chain
import hashlib
import calendar
from rest_framework.response import Response
import json
from apps.violations.methods import check_violation_rules_by_date


def open_employee(employee_id):
    """
    Возвращает объект AgencyEmployee по его ID
    """
    if not employee_id:
        return None
    try:
        employee_id = int(employee_id)
    except:
        return None
    return AgencyEmployee.objects.filter(id=employee_id).first()


def open_employee_doc(doc_id):
    """
    Возвращает объект EmployeeDoc по его ID
    """
    if not doc_id:
        return None
    try:
        doc_id = int(doc_id)
    except:
        return None
    return EmployeeDoc.objects.filter(id=doc_id).first()


def open_employee_job_history(job_history_id):
    """
    Возвращает объект JobHistory по его ID
    """
    if not job_history_id:
        return None
    try:
        job_history_id = int(job_history_id)
    except:
        return None
    return JobHistory.objects.filter(id=job_history_id).first()


def employees_by_number(agency, number):
    """
    Поиск cотрудников по агентству и внутреннему табельному номеру
    """
    return AgencyEmployee.objects.filter(agency=agency, number=number)


def employees_by_ext_number(headquarter, agency, ext_number):
    """
    Поиск сотрудников по агентству и внешнему табельному номеру
    """
    query = OrgHistory.objects.filter(headquater=headquarter, number=ext_number)
    ids = query.filter(agency_employee__agency=agency).values_list('agency_employee_id', flat=True)
    return AgencyEmployee.objects.filter(id__in=ids)


def employees_duplicates(on_date, surname, firstname, patronymic, date_of_birth):
    """
    Поиск дубликатов сотрудников по ФИО и дате рождения, работающих дату on_date.
    """
    # Т.к. в соответствии с требованиями SAP один и тот же сотрудник не может быть уволен из одного агентства и принят в другое
    # в один день, то поиск сотрудника осуществляем на день до заданного в параметре on_date
    min_dismissal_date = on_date - datetime.timedelta(days=1)
    q = AgencyEmployee.objects.all()
    query = AgencyEmployee.objects.filter(firstname=firstname, surname=surname, patronymic=patronymic,
                                          date_of_birth=date_of_birth)
    return query.filter(Q(dismissal__isnull=True) | Q(dismissal__gte=min_dismissal_date))

def get_emp_id(employees, current_user, agency_pages):


    emp_id_html = []
    for i in employees:
        if check_struct_access_to_page(current_user, i.agency.headquater, i.agency, agency_pages, 'read'):
            emp_id_html.append(f"<a href='/employee/{str(i.id)}'> <b style='color: #FFD700'> Редактировать </b>")
        else:
            emp_id_html.append(f"<b style='color: #FFD700'> {str(i.id)} </b>")


        print('get_emp:',emp_id_html)
    if len(employees) == 1:
        emp_id_html = emp_id_html[0]

    return emp_id_html


def check_employee_medical(employee, date=None):
    """ Метод проверяет наличие у сотрудника employee действующей медицинской книжки на дату date """
    on_date = date if date else timezone.now().date()
    # Допускается работа без медицинской книжки первые 14 дней с момента приема в агентство
    if (on_date - employee.receipt).days <= 14:
        return True
    # Поиск медицинкой книжки
    query = EmployeeDoc.objects.filter(agency_employee=employee, doc_type__code='medical')
    query = query.filter(start__lte=date, end__gte=date)
    if query.exists():
        return True
    # Условия не выполнены
    return False


def employee_job_history(employee, date=None):
    """ Метод возвращает список назачений должности сотруднику employee на дату date """
    on_date = date if date else timezone.now().date()
    query = JobHistory.objects.filter(agency_employee=employee, start__lte=on_date)
    return query.filter(Q(end__gte=on_date) | Q(end__isnull=True))


def employee_jobs(employee, date=None):
    """ Метод возвращает список должностей сотрудника employee, действующий на дату date """
    ids = employee_job_history(employee, date).values_list('job_id', flat=True)
    return Job.objects.filter(id__in=ids)


def employee_clients(employee, date=None):
    """ Метод возвращает список клиентов, в которых может работать сотрудник employee на дату date """
    on_date = date if date else timezone.now().date()
    query = OrgHistory.objects.filter(agency_employee=employee, start__lte=on_date)
    query = query.filter(Q(end__gte=on_date) | Q(end__isnull=True))
    ids = query.order_by('headquater_id').distinct('headquater_id').values_list('headquater_id', flat=True)
    return Headquater.objects.filter(party='client', id__in=ids)


def attach_employee(user, employee, recruitment_date, organization):
    """
    Прикрепить сотрудника агентства к клиенту. Параметры метода:
    - user - текущий пользователь, от имени которого выполняется операция
    - employee - сотрудник агентства
    - recruitment_date - дата прикрепления сотрудника
    - organization - организация клиента
    """

    # Проверяем, что агентство может поставлять людей в выбранную организацию
    agency = employee.agency
    headquarter = organization.headquater
    organizations = cities_by_agency(agency, headquarter)
    if not organization in organizations:
        return None

    # Дата прикрепления не может быть меньше даты приема сотрудника в агентство
    if recruitment_date < employee.receipt:
        cur_recruitment_date = employee.receipt
    else:
        cur_recruitment_date = recruitment_date

    # Проверяем, что сотрудник еще не прикреплен к организации клиента, т.е. отсутствует OrgHistory с 
    # незакрытой датой завершения
    query = OrgHistory.objects.filter(agency_employee=employee, organization=organization, headquater=headquarter,
                                      end__isnull=True)
    if query.exists():
        return None
    # Если на выбранную дату есть OrgHistory с заданной датой завершения, то и выбранная дата приема меньше даты завершения + 2 дня,
    # то корректируем дату начала 
    query = OrgHistory.objects.filter(agency_employee=employee, organization=organization, headquater=headquarter,
                                      end__isnull=False)
    if query.exists():
        max_date = query.aggregate(Max('end'))['end__max'] + datetime.timedelta(days=2)
        if max_date >= cur_recruitment_date:
            cur_recruitment_date = max_date

    # Проверяем, что по данному сотруднику нет запросов на прием сотрудника без ответа
    query = EmployeeEvent.objects.filter(agency_employee=employee, organization=organization, headquater=headquarter)
    query = query.filter(kind='recruitment', answer_received=False)
    if query.exists():
        return None

    # Если в день приема было мероприятие увольнения, то сдвигаем дату приема на 1 день в будущее
    query = EmployeeEvent.objects.filter(agency_employee=employee, organization=organization, headquater=headquarter,
                                         kind='dismissal')
    if query.exists():
        max_date = query.aggregate(Max('dismissal_date'))['dismissal_date__max']
        if max_date >= recruitment_date:
            cur_recruitment_date = max_date + datetime.timedelta(days=1)

    # Создаем событие приема
    return EmployeeEvent.objects.create(
        user=user,
        agency_employee=employee,
        agency=agency,
        kind='recruitment',
        headquater=headquarter,
        organization=organization,
        recruitment_date=cur_recruitment_date,
        answer_received=False
    )


def accept_employee_attach(user, event, recruitment_state, recruitment_date, ext_number):
    """
    Подтвердить прикрепление сотрудника агентства к клиенту. Параметры метода:
    - user - текущий пользователь, от имени которого выполняется операция
    - event - событие, инициировавшее запрос на прикрепление сотрудника
    - recruitment_state - состояние активации сотрудника, возможные значеия active и inactive
    - recruitment_date - дата приема
    - ext_number - табельный номер сотрудника в системе 
    """
    # ПРОВЕРКА ПАРАМЕТРОВ
    if event.kind != 'recruitment':
        return f'Event {event.guid} is not recruitment'
    # Проверяем, не занят ли присвоенный табельный номер другим сотрудником
    employees = employees_by_ext_number(event.headquater, event.agency, ext_number)
    if employees.exists() and event.agency_employee not in employees:
        return f'externalNumber {ext_number} for employee {event.agency_employee.id} is occupied by employee {employees.first().id}'
    
    # ОСНОВНОЙ ФУНКЦИОНАЛ
    is_inactive = False if recruitment_state == 'active' else True
    # - проверяем, есть ли в базе информация о прикреплении сотрудника к данному клиенту и орг. единице
    query = OrgHistory.objects.filter(headquater=event.headquater, organization=event.organization, agency_employee=event.agency_employee)
    query = query.filter(Q(start=recruitment_date) | Q(end__isnull=True))
    count = query.count()
    # - если в БД числится 2 и более записей о прикреплении сотрудник
    if count >= 2:
        return f'Employee {event.agency_employee.number} has several active OrgHistory to {event.headquater} \ {event.organization}'
    # - информация о прикреплении сотрудника была получена ранее
    elif count == 1:
        
        # Пропускаем, если состояние прикрепления не изменилось
        orghistory = query.first()
        if orghistory.is_inactive == is_inactive:
            return None
        # Обновляем основные поля карточи
        orghistory.is_inactive = is_inactive
        orghistory.number = ext_number
        orghistory.save(update_fields=['is_inactive', 'number'])
        
    # - информации о прикреплении сотрудника нет
    else:
    
        # Добавляем в события, связанные с данным сотрудником, присвоенный внешний табельный номер. Это необходимо
        # для корректной передачи событий, созданных между прикреплением сотрудника и получением подтверждения из SAP
        EmployeeEvent.objects.filter(
            agency_employee=event.agency_employee,
            headquater=event.headquater,
            ext_number__isnull=True,
            dt_created__gt=event.dt_created
        ).update(ext_number=ext_number)
        
        # Закрепляем внешний номер за сотрудником
        OrgHistory.objects.create(
            headquater=event.headquater,
            organization=event.organization,
            agency_employee=event.agency_employee,
            number=ext_number,
            start=recruitment_date,
            is_inactive=is_inactive
        )
    
    # ДОПОЛНИТЕЛЬНЫЕ ОПЕРАЦИИ
    # - фиксируем событие подтверждения регистрации
    event_history = EmployeeHistory.objects.create(
        user=user,
        headquater=event.headquater,
        organization=event.organization,
        event=event,
        agency_employee=event.agency_employee,
        agency=event.agency,
        kind='accept_recruitment',
        recruitment_state=recruitment_state,
        recruitment_date=recruitment_date,
        ext_number=ext_number
    )
    # -если сотрудник был ранее включен в черный список, а теперь принят, то флаг снимаем
    blacklist_events = event.agency_employee.get_blacklisted_events().filter(headquater=event.headquater)
    if blacklist_events.exists():
        blacklist_events.update(blacklist=False)
    # - фиксируем получение ответа по событию (TODO - отказаться от данного похода)
    event.answer_received = True
    event.save(update_fields=['answer_received'])
    return None


def reject_employee_attach(user, event, reject_reason):
    """
    Отклонить прикрепление сотрудника агентства к клиенту. Параметры метода:
    - user - текущий пользователь, от имени которого выполняется операция
    - event - событие, инициировавшее запрос на прикрепление сотрудника
    - reject_reason - причина отклонения
    """
    # Проверка параметров
    if event.kind != 'recruitment':
        return f'Event {event.guid} is not recruitment'
    if event.answer_received:
        return None

    # Удаляем события, связанные с данным сотрудником и созданные между прикреплением сотрудника и получением
    # отказа из SAP. Удаляем, т.к. без внешнего табельного номера обработка таких событий невозможна.
    EmployeeEvent.objects.filter(
        agency_employee=event.agency_employee,
        headquater=event.headquater,
        ext_number__isnull=True,
        dt_created__gt=event.dt_created
    ).delete()

    # Фиксируем событие отклонения регистрации
    event_history = EmployeeHistory.objects.create(
        user=user,
        headquater=event.headquater,
        organization=event.organization,
        event=event,
        agency_employee=event.agency_employee,
        agency=event.agency,
        kind='reject_recruitment',
        recruitment_state='inactive',
        reject_reason=reject_reason
    )

    # Фиксируем получение ответа
    event.answer_received = True
    event.save(update_fields=['answer_received'])
    return None


def dismiss_employee(user, employee, dismissal_date, dismissal_reason, blacklist=False, headquarter=None,
                     organization=None):
    """
    Увольнение сотрудника employee от имени пользователя user. Другие параметры метода:
    - dismissal_date - дата увольнения (считаем, что начиная с указанной даты сотрудник уже не работает)
    - dismissal_reason - причина увольнения
    - blacklist - включение в черный список (по умолчанию False)
    - headquarter - компания-клиент, откуда увольняем сотрудника, если не задана, то увольняем из всех
    """
    # Определяем список подразделений, в которых числится сотрудник
    org_history_list = OrgHistory.objects.filter(agency_employee=employee, end__isnull=True)
    if headquarter:
        org_history_list = org_history_list.filter(headquater=headquarter)
    if organization:
        org_history_list = org_history_list.filter(organization=organization)
    for org_history in org_history_list:
        # Дата события увольнения должна быть хотя бы через день после приема
        cur_dismissal_date = dismissal_date if dismissal_date > org_history.start else org_history.start + datetime.timedelta(
            days=1)

        # Создаем событие на увольнение сотрудника
        EmployeeEvent.objects.create(
            user=user,
            agency_employee=employee,
            agency=employee.agency,
            kind='dismissal',
            headquater=org_history.headquater,
            organization=org_history.organization,
            ext_number=org_history.number,
            dismissal_date=cur_dismissal_date,
            dismissal_reason=dismissal_reason,
            blacklist=blacklist
        )
        # Ищем смены данного сотрудника после даты увольнения и снимаем назначение
        OutsourcingShift.objects.filter(agency_employee=employee, headquater=org_history.headquater,
                                        start_date__gte=cur_dismissal_date).update(agency_employee=None,
                                                                                   dt_change=timezone.now())
        PromoShift.objects.filter(agency_employee=employee, headquarter=org_history.headquater,
                                  start_date__gte=cur_dismissal_date).update(agency_employee=None,
                                                                             dt_change=timezone.now())
        # Устанавливем дату завершения привязки к магазину, на 1 день меньше, т.к. в org_history храним последний рабочий день
        org_history.end = cur_dismissal_date - datetime.timedelta(days=1)
        org_history.save(update_fields=['end'])

    # Ищем все кадровые мероприятия (recruitment) данного сотрудника, по которым еще не получили подтверждение и формируем событие на увольненеи
    event_list = EmployeeEvent.objects.filter(agency_employee=employee, kind='recruitment', answer_received=False)
    if headquarter:
        event_list = event_list.filter(headquater=headquarter)
    if organization:
        org_history_list = org_history_list.filter(organization=organization)
    for event in event_list:
        # Пропускаем, если последнее событие по сотруднику также является событием на открепление (чтобы не было дублирования)
        last_event = EmployeeEvent.objects.filter(agency_employee=employee, headquater=event.headquater).last()
        if last_event and last_event.kind == 'dismissal':
            continue
        # Дата события увольнения должна быть хотя бы через день после события приема
        cur_dismissal_date = dismissal_date if dismissal_date > event.recruitment_date else event.recruitment_date + datetime.timedelta(
            days=1)
        EmployeeEvent.objects.create(
            user=user,
            agency_employee=employee,
            agency=event.agency,
            kind='dismissal',
            headquater=event.headquater,
            organization=event.organization,
            dismissal_date=cur_dismissal_date,
            dismissal_reason=dismissal_reason,
            blacklist=blacklist
        )

    # Обновляем дату увольнения у сотрудника
    if not headquarter:
        # dismissal в карточке сотрудника - последний рабочий день, а dissmissal_date - дата увольнения, т.е. первый не рабочий день
        employee.dismissal = dismissal_date - datetime.timedelta(
            days=1) if dismissal_date > employee.receipt else employee.receipt
        employee.save(update_fields=['dismissal'])


def on_change_employee(user, employee, kind, event_date, previous_instance=None):
    """
    Изменение персональных данных сотрудника employee пользователем user. Другие параметры метода:
    - kind - вид события, возможные значения 'change' и 'agency'
    - event_date - дата события
    """
    # Определяем список подразделений клиента, в которых числится сотрудник
    org_history_list = OrgHistory.objects.filter(agency_employee=employee, start__lte=event_date)
    org_history_list = org_history_list.filter(Q(end__gte=event_date) | Q(end__isnull=True))
    for org_history in org_history_list:
        # Создаем событие на изменение персональных данных
        diff = employee.get_diff(previous_instance)
        EmployeeEvent.objects.create(
            user=user,
            agency_employee=employee,
            agency=employee.agency,
            kind=kind,
            headquater=org_history.headquater,
            organization=org_history.organization,
            ext_number=org_history.number,
            params=diff
        )

    # Ищем все кадровые мероприятия (recruitment) данного сотрудника, по которым еще не получили подтверждение
    event_list = EmployeeEvent.objects.filter(agency_employee=employee, kind='recruitment', answer_received=False)
    for event in event_list:
        EmployeeEvent.objects.create(
            user=user,
            agency_employee=employee,
            agency=event.agency,
            kind=kind,
            headquater=event.headquater,
            organization=event.organization
        )


def make_orghistory_search(search=None):
    """Поиск по внешнему ТН в orghistory"""
    query_set = OrgHistory.objects.all()
    if search:
        query_set = query_set.filter(Q(number__icontains=search))
    return query_set.order_by('agency_employee_id').distinct('agency_employee_id').values_list('agency_employee_id',
                                                                                               flat=True)


def make_search(query_set, search=None):
    """Поиск по ФИО, ТН и внешнему ТН"""
    if search:
        search_list = search.split(" ")
        for ss in search_list:
            if not ss or len(ss) < 3:
                continue
            orghistory_agency_employee_ids = make_orghistory_search(ss)
            query_set = query_set.filter(Q(surname__icontains=ss) |
                                         Q(firstname__icontains=ss) |
                                         Q(patronymic__icontains=ss) |
                                         Q(number__icontains=ss) |
                                         Q(id__in=orghistory_agency_employee_ids))
    return query_set


def make_headquarter_emp_ids(date, headquarter=None, unit=None):
    query_set = OrgHistory.objects.all()
    # Фильтруем по дате уже в другом месте
    # query_set = query_set.filter(Q(start__lte=date) & (Q(end__gte=date) | Q(end__isnull=True)))

    # Определяем период по дате для фильтра по магазину
    if not date:
        date = timezone.now().date()
    else:
        if not isinstance(date, datetime.date):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    month_start = date
    month_end = month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1])

    if headquarter:
        query_set = query_set.filter(headquater=headquarter)
    if unit:
        if unit.kind != 'store':
            query_set = query_set.filter(Q(organization=unit) | Q(organization__parent=unit))
        else:
            # Получаем список смен сотрудников, которые работают или работали в этом магазине
            total_emp_ids = set()
            shift_emp_ids = OutsourcingShift.objects.filter(request__organization=unit,
                                                            agency_employee__isnull=False,
                                                            start_date__gte=month_start,
                                                            start_date__lte=month_end). \
                order_by('agency_employee_id').distinct('agency_employee_id'). \
                values_list('agency_employee_id', flat=True)
            total_emp_ids.update(shift_emp_ids)
            promo_emp_ids = PromoShift.objects.filter(organization=unit,
                                                      agency_employee__isnull=False,
                                                      start_date__gte=month_start,
                                                      start_date__lte=month_end). \
                order_by('agency_employee_id').distinct('agency_employee_id'). \
                values_list('agency_employee_id', flat=True)
            total_emp_ids.update(promo_emp_ids)
            return total_emp_ids
    query_set = query_set.order_by('agency_employee_id').distinct('agency_employee_id').values_list(
        'agency_employee_id', flat=True)
    return query_set


def make_emp_queryset(unit_headquarter=None, unit=None, date=None):
    """Формирование queryset сотрудников"""
    if not date:
        date = timezone.now().date()
    else:
        if not isinstance(date, datetime.date):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    """Ограничиваем по клиенту и орг. единице"""
    if unit_headquarter.party in ['agency', 'promo', 'broker']:
        emp_query_set = AgencyEmployee.objects.filter(agency__headquater=unit_headquarter)
        if unit:
            emp_query_set = emp_query_set.filter(ae_history__agency=unit)
            # emp_query_set = emp_query_set.filter(
            #         Q(ae_history__start__lte=date, ae_history__end__isnull=True) | Q(ae_history__start__lte=date,
            #                                                                          ae_history__end__gte=date))
            # emp_query_set = emp_query_set.filter(agency=unit)
    else:
        # TODO убедиться, что дата более не нужна и убрать
        emp_query_set = AgencyEmployee.objects.filter(id__in=make_headquarter_emp_ids(date, unit_headquarter, unit))

    return emp_query_set


def make_emp_data(page_codes, agency_employee, date=None, headquarter=None):
    """Формирование данных по сотруднику"""
    if not date:
        date = timezone.now().date()
    else:
        if not isinstance(date, datetime.date):
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

    emp_data = dict()
    # Основная информация по сотруднику
    emp_data['id'] = agency_employee.id
    emp_data['name'] = agency_employee.name
    emp_data['number'] = agency_employee.number
    emp_data['agency'] = agency_employee.agency.name
    emp_data['external_number'] = agency_employee.external_number
    emp_data['date_of_birth'] = agency_employee.date_of_birth.isoformat() if agency_employee.date_of_birth else None
    emp_data[
        'medical_end_date'] = agency_employee.medical_end_date.isoformat() if agency_employee.medical_end_date else None

    # Дополнительная
    jobs_list_by_date = agency_employee.get_jobs_list_by_date(date)
    emp_data['jobs'] = list(jobs_list_by_date)

    # Для клиента
    if headquarter.party == 'client':
        orgs_list_by_date = agency_employee.get_orgs_list_by_headquarter(headquarter)
        emp_data['organizations'] = list(orgs_list_by_date)
        emp_data['violations'] = check_violation_rules_by_date(page_codes, headquarter, agency_employee, date)
        emp_data['start_date'] = agency_employee.get_client_start(
            headquarter).isoformat() if agency_employee.get_client_start(headquarter) else None
        emp_data['end_date'] = agency_employee.get_client_end(
            headquarter).isoformat() if agency_employee.get_client_end(headquarter) else None

    # Для агентства
    else:
        # Должности которые имеет на дату
        jobs_list_by_date = agency_employee.get_jobs_list_by_date(date)
        # Организации в которых работал/работает сотрудник
        orgs_list_by_date = agency_employee.get_organizations()
        # Открытые мероприятитя приема, на которые еще не поступил ответ
        open_recruitment_events = agency_employee.get_open_recruitment_events()
        # Закрытые orghistory на дату
        closed_orghistory = agency_employee.get_closed_orghistory(date)

        # Добавляем к сотруднику
        emp_data['jobs'] = list(jobs_list_by_date)
        emp_data['organizations'] = list(orgs_list_by_date)
        emp_data['open_recruitment_events'] = list(open_recruitment_events)
        emp_data['closed_orghistory'] = list(closed_orghistory)
        emp_data['violations'] = check_violation_rules_by_date(page_codes, headquarter, agency_employee, date)

        if agency_employee.receipt <= date and (agency_employee.dismissal is None or agency_employee.dismissal >= date):
            emp_data['state'] = 'active'
        else:
            emp_data['state'] = 'dismissed'
        emp_data['start_date'] = agency_employee.receipt.isoformat() if agency_employee.receipt else None
        emp_data['end_date'] = agency_employee.dismissal.isoformat() if agency_employee.dismissal else None
    return emp_data


def violation_level_employees(queryset, violationlevel=None, date=None):
    if not violationlevel:
        return queryset

    if not date:
        date = timezone.now().date()

    # Определения нарушения по которому будет идти проверка
    violationrule = violationlevel.rule

    # и границы дат
    min_find_date = date + timedelta(days=violationlevel.value_from)
    max_find_date = date + timedelta(days=violationlevel.value_to)

    # ид для поиска по документам
    employee_ids = queryset.values_list('id', flat=True)

    """Обработка в зависимости от кода нарушения"""
    if violationrule.code == 'medical':
        # Проверка наличия действующей мед. книжки
        # Определяем минимальную дату приема с которой медкнижка должна быть
        min_receipt_date = date - timedelta(days=14)
        # сотрудники с даты приема которых прошло более 14 дней
        queryset = queryset.filter(receipt__lte=min_receipt_date)
        # сотрудники у которых есть мед. книжка
        employee_medical_ids = EmployeeDoc.objects.filter(doc_type__code='medical',
                                                          end__gte=min_find_date,
                                                          end__lte=max_find_date,
                                                          agency_employee_id__in=employee_ids). \
            values_list('agency_employee_id', flat=True)
        queryset = queryset.filter(id__in=employee_medical_ids)

    if violationrule.code == 'blacklist':
        # Проверка событий EmployeeEvent с флагом включения в blacklist
        employee_blacklisted_ids = EmployeeEvent.objects.filter(agency_employee_id__in=employee_ids, blacklist=True). \
            values_list('agency_employee_id', flat=True)
        queryset = queryset.filter(id__in=employee_blacklisted_ids)

    # TODO пока оставляем, но правило не используем
    if violationrule.code == 'dismissed_by_agency':
        # Проверка даты увольенения сотрудника из агентства
        # сотрудники с даты приема которых прошло менее 14 дней
        queryset = queryset.filter(dismissal__gte=min_find_date, dismissal__lte=max_find_date)

    # TODO пока оставляем, но правило не используем
    if violationrule.code == 'dismissed_by_client':
        # Проверка наличия заканчивающихся авторизаций у клиента
        employee_closing_ids = OrgHistory.objects.filter(agency_employee_id__in=employee_ids,
                                                         end__gte=min_find_date,
                                                         end__lte=max_find_date). \
            values_list('agency_employee_id', flat=True)
        queryset = queryset.filter(id__in=employee_closing_ids)

    if violationrule.code == 'wait_register':
        # Проверка событий приема, на которые не поступил ответ
        min_find_date = date - timedelta(days=violationlevel.value_to)
        max_find_date = date - timedelta(days=violationlevel.value_from)
        min_find_dtime = make_aware(datetime.datetime.combine(min_find_date, datetime.datetime.min.time()),
                                    timezone=pytz.timezone(TIME_ZONE))
        max_find_dtime = make_aware(datetime.datetime.combine(max_find_date, datetime.datetime.max.time()),
                                    timezone=pytz.timezone(TIME_ZONE))
        employee_wait_ids = EmployeeEvent.objects.filter(agency_employee_id__in=employee_ids,
                                                         kind='recruitment',
                                                         answer_received=False,
                                                         dt_created__gte=min_find_dtime,
                                                         dt_created__lte=max_find_dtime). \
            values_list('agency_employee_id', flat=True)
        queryset = queryset.filter(id__in=employee_wait_ids)
    return queryset


def get_shift_violation_employee_ids(shifts=None):
    if not shifts:
        return []
    shift_employee_ids = shifts.order_by('agency_employee_id').distinct('agency_employee_id').values_list(
        'agency_employee_id', flat=True)

    recent_employees = AgencyEmployee.objects.filter(id__in=shift_employee_ids).values_list('id', 'receipt')

    medical_employee_ids = EmployeeDoc.objects.filter(agency_employee_id__in=shift_employee_ids,
                                                      doc_type__code='medical',
                                                      end__isnull=False).order_by('agency_employee_id', '-end'). \
        distinct('agency_employee_id').values_list('agency_employee_id', 'end')
    result_emp_dict = dict()
    for employee in recent_employees:
        result_emp_dict.update({employee[0]: employee[1] + timedelta(days=14)})
    for employee in medical_employee_ids:
        result_emp_dict.update({employee[0]: employee[1]})
    return result_emp_dict


def get_period_violation_employee_ids(employees=None, start=None, end=None, files_check=False):
    employee_ids = employees.values_list('id', flat=True)
    if not start or not end:
        return []
    start_date = start.date()
    end_date = end.date()
    # Проверка по мед. книжки
    min_receipt_date = start_date - timedelta(days=14)
    recent_employee_ids = AgencyEmployee.objects.filter(id__in=employee_ids, receipt__gte=min_receipt_date).values_list(
        'id', flat=True)
    medical_employee_ids = EmployeeDoc.objects.filter(agency_employee_id__in=employee_ids,
                                                      doc_type__code='medical',
                                                      start__lte=start_date,
                                                      end__gte=end_date)
    # Проверка файлов мед. книжки
    if files_check:
        medical_employee_ids = medical_employee_ids.filter(has_files=True)

    medical_employee_ids = medical_employee_ids.order_by('agency_employee_id'). \
        distinct('agency_employee_id').values_list('agency_employee_id', flat=True)

    total_employee_ids = set(chain(recent_employee_ids, medical_employee_ids))
    return total_employee_ids


def get_verme_docs():
    return RemoteService.objects.filter(code='VermeDocs').first()


def check_verme_docs():
    service = get_verme_docs()
    if service:
        return True, service.endpoint, service.login
    return False, None, None


def make_docs_params(user, guid=None):
    params = dict()
    service = get_verme_docs()
    if service and guid:
        timestamp = timezone.now().isoformat()
        username = user.username
        login = service.login
        key = service.params.get('authorize_key')
        if not key:
            return params
        hash_string = timestamp + str(guid) + username + login + key
        hash_value = hashlib.md5(hash_string.encode()).hexdigest()
        params.update({"timestamp": timestamp, "login": login, "hash": hash_value, "username": username})
    return params


def get_medical_docs(request, employee_list, agency_pages=None, client_pages=None, unit_headquarter=None):
    current_user = request.user
    docs_service = get_verme_docs()
    if not docs_service:
        return make_error_response('Undefined: docs_service')

    start = request.GET.get('start')
    end = request.GET.get('end')
    month = request.GET.get('month')

    if unit_headquarter:
        headquarter_max_files_count = Config.objects.filter(headquater=unit_headquarter,
                                                            key='max_files_from_docs').first()
        max_files_count = int(headquarter_max_files_count.value) if headquarter_max_files_count else 200
    else:
        max_files_count = 200

    doc_guids = list()
    added_files_count = 0

    if isinstance(employee_list, list):
        employee_list = AgencyEmployee.objects.filter(id__in=employee_list)

    # Если передан период
    if (start and end) or month:
        employee_docs = EmployeeDoc.objects.filter(doc_type__code='medical', agency_employee__in=employee_list)
        if start and end:
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            end = datetime.datetime.strptime(end, '%Y-%m-%d').date()
            employee_docs = employee_docs.filter(start__lte=start, end__gte=end)
        if month:
            month_start = datetime.datetime.strptime(month, '%Y-%m-%d').date()
            month_max_day = calendar.monthrange(month_start.year, month_start.month)[1]
            month_end = month_start.replace(day=month_max_day)
            employee_docs = employee_docs.filter(start__lte=month_start, end__gte=month_end)
        employee_docs = employee_docs.select_related('agency_employee').order_by('agency_employee_id', '-end'). \
            distinct('agency_employee_id')

        for doc in employee_docs:
            # ПРОВЕРКА ПРАВ ДОСТУПА
            has_access = False
            # - проврка доступа для сотрудника агентства
            if check_struct_access_to_page(current_user, doc.agency_employee.agency.headquater,
                                           doc.agency_employee.agency, agency_pages,
                                           'read'):
                has_access = True
            # - проверка доступа для сотрудника клиента
            if not has_access:
                clients = employee_clients(doc.agency_employee)
                for client_headquarter in clients:
                    if check_struct_access_to_page(current_user, client_headquarter, None, client_pages, 'read'):
                        has_access = True
                        break
            if not has_access:
                return make_error_response('AccessDenied')

            if added_files_count > max_files_count:
                return Response({'type': 'error', 'message': 'maxFilesCountLimit'})
            doc_guids.append(str(doc.guid))
            added_files_count += 1
    else:
        # Если не передан период, возвращаем на текущую дату документ с максимальным сроком действия
        # Последовательно обходим переданных сотрудников и запрашиваем по ним документы
        for employee in employee_list:
            # ПРОВЕРКА ПРАВ ДОСТУПА
            has_access = False
            # - проврка доступа для сотрудника агентства
            if check_struct_access_to_page(current_user, employee.agency.headquater, employee.agency, agency_pages,
                                           'read'):
                has_access = True
            # - проверка доступа для сотрудника клиента
            if not has_access:
                clients = employee_clients(employee)
                for client_headquarter in clients:
                    if check_struct_access_to_page(current_user, client_headquarter, None, client_pages, 'read'):
                        has_access = True
                        break
            if not has_access:
                return make_error_response('AccessDenied')

            # Для каждого сотрудника находим мед книжку с максимальным сроком действия
            if employee.last_medical_guid:
                if added_files_count > max_files_count:
                    return Response({'type': 'error', 'message': 'maxFilesCountLimit'})
                doc_guids.append(employee.last_medical_guid)
                added_files_count += 1

    if not doc_guids:
        return Response({'type': 'error', 'message': 'noEntityGuids'})

    # Формируем и отправляем запрос на сервис docs со списком guid требуемых документов
    str_guids = ','.join(doc_guids)
    docs_params = make_docs_params(current_user, str_guids)
    response = docs_service.send_sync_json_request(docs_params,
                                                   'archive',
                                                   entity_guids=json.dumps(doc_guids),
                                                   ip=request.META.get('HTTP_X_REAL_IP'),
                                                   format='json')
    return Response(response)


def get_employee_docs(**kwargs):
    return EmployeeDoc.objects.filter(**kwargs).values_list('agency_employee_id', flat=True)


def get_employee_events(**kwargs):
    return EmployeeEvent.objects.filter(**kwargs).values_list('agency_employee_id', flat=True)


def get_employee_orghistories(**kwargs):
    return OrgHistory.objects.filter(**kwargs).values_list('agency_employee_id', flat=True)


def get_last_agency_history_and_startdate(employee: AgencyEmployee):
    """
    возвращает первую возможную дату, с которой можно сделать перевод
    :param employee:
    :return:
    """
    agency_history = AgencyHistory.objects.filter(agency_employee=employee).order_by('-start').first()
    startdate = agency_history.end if agency_history.end else agency_history.start
    if startdate < datetime.date.today():
        startdate = datetime.date.today()
    return agency_history, startdate + datetime.timedelta(1)
