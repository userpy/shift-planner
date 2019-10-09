from django.utils import timezone
from django.db.models import F
from apps.permission.methods import Page
from .models import ViolationRule, ViolationRuleItem
from datetime import timedelta, datetime


def open_violation(violation_id):
    """Возвращает объект ViolationRule по его ID"""
    if not violation_id:
        return None
    try:
        violation_id = int(violation_id)
    except:
        return None
    return ViolationRule.objects.filter(id=violation_id).first()


def open_violation_level(violation_level_id):
    """Возвращает объект ViolationRule по его ID"""
    if not violation_level_id:
        return None
    try:
        violation_level_id = int(violation_level_id)
    except:
        return None
    return ViolationRuleItem.objects.filter(id=violation_level_id).first()


def make_violations_data(page_codes=None, party=None):
    """Формирование списка нарушений с уровнями"""
    violation_rules = list()
    rules = get_violation_rules(page_codes, party)
    for rule in rules:
        rule_levels = get_violation_rule_levels(rule).values('id', 'name'). \
            annotate(text=F('name')).values('id', 'text')
        if rule_levels:
            violation_rules.append({
                'text': rule.name,
                'children': rule_levels
            })
    return violation_rules


def get_violation_rules(page_codes=None, party=None):
    """Получение списка нарушений для проверки на основе party"""
    if not page_codes:
        return None
    if not party:
        return None
    page_codes = Page.objects.filter(code__in=page_codes, party=party)
    violation_rules = ViolationRule.objects.filter(pages__in=page_codes)
    return violation_rules


def get_violation_rule_levels(violation_rule=None):
    """Получение уровней списка нарушений для проверки на основе нарушения, party"""
    if not violation_rule:
        return None
    violation_rule_levels = ViolationRuleItem.objects.filter(rule=violation_rule)
    return violation_rule_levels


def check_violation_rules_exists_by_date(page_codes=None, agency_employee=None, date=None):
    """Проверка нарушений сотрудника по дате, возвращает True/False"""
    if isinstance(date, datetime):
        date = date.date()

    if not agency_employee or not page_codes:
        return None
    if not date:
        date = timezone.now().date()
    rules = get_violation_rules(agency_employee.agency.headquater.party)
    if not rules:
        return True
    for rule in rules:
        check_result = check_violation_by_date(agency_employee, rule, date)
        if check_result:
            return True
    return False


def check_violation_rules_by_date(page_codes=None, headquarter=None, agency_employee=None, date=None):
    """Проверка нарушений сотрудника по дате, возвращает список нарушений"""
    if not agency_employee or not page_codes or not headquarter:
        return None
    if not date:
        date = timezone.now().date()
    violations_list = list()
    for rule in get_violation_rules(page_codes, headquarter.party):
        check_result = check_violation_by_date(agency_employee, rule, date)
        if check_result:
            violations_list.append(check_result)
    return violations_list


def check_violation_level_by_value(violationrule, value, violationlevel=None, unlimited=False):
    """Возвращает уровень нарушения для заданного значения"""
    # для нарушений, где диапазона нет
    if unlimited:
        affected_level = violationrule.violationruleitem_set.filter(value_to__lte=value)
    else:
        affected_level = violationrule.violationruleitem_set.filter(value_from__lte=value, value_to__gte=value)
    if violationlevel:
        affected_level = affected_level.filter(id=violationlevel.id)
    affected_level = affected_level.order_by('-value_from', '-value_to').first()
    return affected_level


def check_violation_by_date(agency_employee=None, violationrule=None, date=None):
    """Проверка конкретного нарушения конкретного острудника на конкретную дату"""
    if not agency_employee or not violationrule:
        return None
    if not date:
        date = timezone.now().date()

    violationlevel = None
    result = dict()

    if isinstance(violationrule, ViolationRuleItem):
        violationlevel = violationrule
        violationrule = violationrule.rule

    """Обработка в зависимости от кода нарушения"""
    if violationrule.code == 'medical':
        # Проверка наличия действующей мед. книжки
        # Определяем минимальную дату приема с которой медкнижка должна быть
        min_receipt_date = date - timedelta(days=14)
        # Определяем дату окончания медкнижки
        medical_end_date = agency_employee.medical_end_date
        # Определяем количество дней до окончания медкнижки
        if agency_employee.receipt < min_receipt_date:
            if medical_end_date:
                valid_for_days = medical_end_date - date
                valid_for_days = int(valid_for_days.total_seconds() / 86400)
            else:
                valid_for_days = 0
            affected_level = check_violation_level_by_value(violationrule, valid_for_days, violationlevel)
            if affected_level:
                result.update({
                    'level': affected_level.severity,
                    'days': valid_for_days,
                    'message': f'{affected_level.message}'
                })

    if violationrule.code == 'blacklist':
        # Проверка событий EmployeeEvent с флагом включения в blacklist
        blacklist_events = agency_employee.get_blacklisted_events()
        if blacklist_events.exists():
            # Получаем список компаний, включивших сотрудника в черный список
            affected_events = blacklist_events.values_list('headquater__name', flat=True)
            if affected_events:
                days = -1
                affected_level = check_violation_level_by_value(violationrule, days, violationlevel)
                if affected_level:
                    blacklist_clients = ",".join(affected_events)
                    result.update({
                        'level': affected_level.severity,
                        'days': days,
                        'message': f'{affected_level.message}: {blacklist_clients}'
                    })

    # TODO пока оставляем, но правило не используем
    if violationrule.code == 'dismissed_by_agency':
        # Проверка даты увольенения сотрудника из агентства
        if agency_employee.dismissal:
            # Получаем количество дней до даты увольенения
            days_delta = agency_employee.dismissal - date
            days_delta = int(days_delta.total_seconds() / 86400)
            affected_level = check_violation_level_by_value(violationrule, days_delta, violationlevel)
            if affected_level:
                result.update({
                    'level': affected_level.severity,
                    'days': days_delta,
                    'message': f'{affected_level.message}'
                })

    # TODO пока оставляем, но правило не используем
    if violationrule.code == 'dismissed_by_client':
        # Проверка наличия заканчивающихся авторизаций у клиента
        closed_orghistory = agency_employee.get_closing_orghistories_by_date(date)
        if closed_orghistory.exists():
            # Получаем самое раннее событие, на которое не поступил ответ
            affected_event = closed_orghistory.filter(end__lte=date).order_by('end_date').first()
            if affected_event:
                days_delta = affected_event.end - date
                days_delta = int(days_delta.total_seconds() / 86400)
                affected_level = check_violation_level_by_value(violationrule, days_delta, violationlevel)
                if affected_level:
                    result.update({
                        'level': affected_level.severity,
                        'days': days_delta,
                        'message': f'{affected_level.message}'
                    })

    if violationrule.code == 'wait_register':
        # Проверка событий приема, на которые не поступил ответ
        open_recruitment_events = agency_employee.open_recruitment_events()
        if open_recruitment_events.exists():
            # Получаем самое раннее событие, на которое не поступил ответ
            affected_event = open_recruitment_events.filter(dt_created__lte=date).first()
            if affected_event:
                days_delta = date - affected_event.dt_created.date()
                days_delta = int(days_delta.total_seconds() / 86400)
                affected_level = check_violation_level_by_value(violationrule, days_delta, violationlevel)
                if affected_level:
                    result.update({
                        'level': affected_level.severity,
                        'days': days_delta,
                        'message': f'{affected_level.message}'
                    })

    if violationrule.code == 'employee_no_shifts':
        # Получаем последнюю смену сотрудника
        affected_shift = agency_employee.latest_shift()

        if affected_shift:
            days_delta = date - affected_shift.start_date
            days_delta = int(days_delta.total_seconds() / 86400)
            affected_level = check_violation_level_by_value(violationrule, days_delta, violationlevel,unlimited=True)
            if affected_level:
                result.update({
                    'level': affected_level.severity,
                    'days': days_delta,
                    'message': f'{affected_level.message}'
                })
        else:
            result.update({
                'level': 'high',
                'days': 0,
                'message': 'Нет ни одной назначенной смены'
            })

    return result


def check_violation_level_by_date(agency_employee=None, violationlevel=None, date=None):
    """Проверка конкретного уровня нарушения конкретного острудника на конкретную дату"""
    if not agency_employee or not violationlevel:
        return None
    if not date:
        date = timezone.now().date()
    return check_violation_by_date(agency_employee, violationlevel, date)
