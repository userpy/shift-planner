#
# Copyright 2018 ООО «Верме»
#
# Файл методов проверки прав доступа
#

from django.contrib.auth.models import User
from apps.lib.utils import content_type_ids_for_models
from apps.outsource.models import Organization, Agency, Headquater
from apps.outsource.methods import get_unit_list_upwards
from .models import Page, AccessProfile, AccessRole, Permission

ACTIONS = ('read', 'write')

""" ******************************* СЕРВИСНЫе методы *********************************** """

def get_page_list_upwards(pages):
    """
    Сервисный метод, принимает на вход объект Page, массив объектов Page, массив кодов страниц или идентификаторов,
    преобразует в массив идентификаторов этих страниц, дополняее вышестоящими по иерархии.
    """
    # Результирующий массив идентификаторов страниц
    page_ids = []

    # Внутренний метод
    def add_page_with_parents(one_page, page_ids):
        page = None
        # Определяем объект страницы
        if type(one_page) == Page:
            page = one_page
        elif type(page) == int:
            page = Page.objects.filter(id=one_page).first()
        else:
            page = Page.objects.filter(code=one_page).first()
        # Добавляем в список саму страницу и родительскую по отношению к ней
        while page and not page.id in page_ids:
            page_ids.append(page.id)
            page = page.parent
    
    # Передан объект страницы
    if type(pages) == Page:
        add_page_with_parents(pages, page_ids)
    # Передан массив объектов или кодов страниц
    else:
        for one_page in pages:
            add_page_with_parents(one_page, page_ids)
    # Возвращаем сформированный массив
    return page_ids

""" ******************************* СТРУКТУРНЫЕ ПОЛНОМОЧИЯ *********************************** """

def check_struct_access(user, headquarter, unit=None):
    """
    Метод возвращает True, если у пользователя есть доступ орг. единице, False - в противном случае.
    Параметры метода:
    - user - текущий пользователь
    - headquarter - выбранный клиент
    - unit - выбранная орг. единица клиента (опциональный)

    """
    # Супер-пользователь может получить доступ к любой орг. единице
    if user.is_superuser:
        return True  
    # Проверем наличие прав доступа на заданного клмента (параметр headquarter)
    user_access = AccessProfile.objects.filter(user=user, headquater=headquarter)
    if not user_access.exists():
        return False
    # Проверяем наличие прав доступа на заданную орг. единицу (параметр unit)
    elif unit:
        user_access = user_access.filter(unit_id__in=get_unit_list_upwards(unit))
        return user_access.exists()
    return True

def check_struct_access_to_page(user, headquarter=None, unit=None, pages=[], action='read'):
    """
    Метож возвращает True, если у пользователя есть уровень доступа на одна из страницу, False - в противном случае.
    Параметры метода:
    - user - текущий пользователь
    - headquarter - выбранный клиент (опциональный)
    - unit - выбранная орг. единица клиента (опциональный)
    - pages - объект страницы или список кодов страниц (оциональный)
    - action - уровень доступа (опциональный)
    """
    # Супер-пользователю разрешено все
    if user.is_superuser:
        return True
    # Определяем список страниц, выходим, если он не задан
    page_ids = get_page_list_upwards(pages)
    if not page_ids:
        return False
    # Выполняем поиск ролей с требуемым уровнем доступа на выбранные страницы, выходим, если таких нет
    roles_ids = Permission.objects.filter(page_id__in=page_ids, action=action).values_list('role_id', flat=True)
    if not roles_ids:
        return False
    # Определяем наличие прав доступа у пользователя на выбранную орг. единицу
    user_access = AccessProfile.objects.filter(user=user, role_id__in=roles_ids)
    if headquarter:
        user_access = user_access.filter(headquater=headquarter)
    if unit:
        user_access = user_access.filter(unit_id__in=get_unit_list_upwards(unit))
    return user_access.exists()

""" ******************************* ПОИСК ДОСТУПНЫХ ОБЪЕКТОВ *********************************** """

def available_pages(user):
    """
    Метод возвращает QuerySet со списком объектов страниц, которые доступны пользователю
    """
    # Для супер-пользователя доступны все страницы
    if user.is_superuser:
        pages = Page.objects.all()
    # Формируем список страниц, доступных пользователю
    else:
        roles_ids = AccessProfile.objects.filter(user=user).values_list('role_id', flat=True)
        pages_ids = Permission.objects.filter(role_id__in=roles_ids).values_list('page_id', flat=True)
        pages = Page.objects.filter(id__in=pages_ids)
    # Убираем из него некорневые и отключенные страницы
    return pages.filter(disabled=False).order_by('sort_key')

def available_headquarters(user, party):
    """
    Метод возвращает QuerySet со списком объектов Headquater заданного вида, которые доступны пользователю
    """
    headquarters = None
    # Для супер-пользователя доступны все клиенты
    if user.is_superuser:
        headquarters = Headquater.objects.all()
    # Формируем список клиентов, доступных пользователю
    else:
        headquarters_ids = AccessProfile.objects.filter(user=user).values_list('headquater_id', flat=True)
        headquarters = Headquater.objects.filter(id__in=headquarters_ids)
    # Если массив не пустой, то убираем из него клиентов с некорректным типом
    if headquarters:
        headquarters = headquarters.filter(party=party).order_by('name')
    return headquarters

def available_sub_units(user, headquarter, unit):
    """
    Метод возвращает QuerySet со списокм объектов организационной структуры, находящихся под объектом unit
    с учетом прав доступа заданного пользователя
    """
    # Выходим, если у пользователя нет доступа к выбранному объекту орг. структуры
    if not headquarter or not check_struct_access(user, headquarter, unit):
        return None
    units = None
    # Орг. структура клиента
    if headquarter.party == 'client':
        # Первый уровень
        if not unit:
            # Орг. единицы верхнего уровня
            if user.is_superuser:
                units = Organization.objects.filter(headquater=headquarter, parent__isnull=True)
            # Орг. единицы, на которые пользователю назначен доступ
            else:
                units_with_direct_access = AccessProfile.objects.filter(user=user).values_list('unit_id', flat=True)
                org_units = Organization.objects.filter(headquater=headquarter, id__in=units_with_direct_access)
        # Остальные уровни
        elif type(unit) == Organization:
            units = Organization.objects.filter(headquater=headquarter, parent=unit)
    # Орг. структура агентства
    else:
        # Первый уровень
        if not unit:
            # Орг. единицы верхнего уровня
            if user.is_superuser:
                units = Agency.objects.filter(headquater=headquarter, parent__isnull=True)
            # Орг. единицы, на которые пользователю назначен доступ
            else:
                units_with_direct_access = AccessProfile.objects.filter(user=user).values_list('unit_id', flat=True)
                units = Agency.objects.filter(headquater=headquarter, id__in=units_with_direct_access)
        # Остальные уровни
        elif type(unit) == Agency:
            units = Agency.objects.filter(headquater=headquarter, parent=unit)
    # Возвращаем итоговый массив
    return units


def available_sel_units(user=None, party=None):
    if not user or not party:
        return None, None

    headquarters_lst = available_headquarters(user, party)
    headquarters_ids = headquarters_lst.values_list('id', flat=True)

    units = None
    if party == 'client':
        # Орг. единицы верхнего уровня
        if user.is_superuser:
            units = Organization.objects.filter(headquater_id__in=headquarters_ids)
        # Орг. единицы, на которые пользователю назначен доступ
        else:
            units_with_direct_access = AccessProfile.objects.filter(user=user).values_list('unit_id', flat=True)
            units = Organization.objects.filter(headquater_id__in=headquarters_ids, id__in=units_with_direct_access)
    # Орг. структура агентства
    else:
        # Орг. единицы верхнего уровня
        if user.is_superuser:
            units = Agency.objects.filter(headquater_id__in=headquarters_ids)
        # Орг. единицы, на которые пользователю назначен доступ
        else:
            units_with_direct_access = AccessProfile.objects.filter(user=user).values_list('unit_id', flat=True)
            units = Agency.objects.filter(headquater_id__in=headquarters_ids, id__in=units_with_direct_access)
    return headquarters_lst, units


def check_permission_by_headquater(request, headquater, page, action):
    if action not in ACTIONS:
        return False
    if not request.user.is_superuser:
        if headquater in get_available_clients_by_user(request.user).values_list('id', flat=True):
            return True
        else:
            return False
    else:
        return True


def check_permission_by_headquater_list(request, headquater_list, page, action):
    if action not in ACTIONS:
        return False
    if not request.user.is_superuser:
        allowed_headquater_list = get_available_clients_by_user(request.user).values_list('id', flat=True)
        for h in headquater_list:
            if h in allowed_headquater_list:
                return True
            else:
                return False
    else:
        return True


def get_available_clients_by_user(user=None, **kwargs):
    """Получение списка доступных пользователю клиентов"""
    if 'username' in kwargs:
        user = User.objects.filter(username=kwargs['username']).first()
    unit_type_id = content_type_ids_for_models(Organization)[0]
    #clients = Organization.objects.filter(parent__isnull=True)
    clients = Headquater.objects.filter(party='client')
    if user.is_superuser:
        return clients.values('id', 'name')
    #profiles = AccessProfile.objects.filter(unit_type_id=unit_type_id, user=user).values_list('unit_id', flat=True)
    profiles = AccessProfile.objects.filter(user=user).values_list('headquater_id', flat=True)
    clients = clients.filter(id__in=profiles)
    return clients.values('id', 'name')


def get_available_companies_by_user(user=None, **kwargs):
    """Получение списка доступных пользователю компаний"""
    if 'username' in kwargs:
        user = User.objects.filter(username=kwargs['username']).first()
    companies = Headquater.objects.all()
    if 'party' in kwargs:
        companies = companies.filter(party=kwargs['party'])
    if user.is_superuser:
        return companies.values('id', 'name', 'party')
    profiles = AccessProfile.objects.filter(user=user).values_list('headquater_id', flat=True)
    companies = companies.filter(id__in=profiles)
    return companies.values('id', 'name', 'party')


def get_client_base_org(headquater):
    """Получение главной организации компании с kind='head'"""
    if type(headquater) == Headquater:
        return Organization.objects.filter(headquater=headquater, kind='head').first()
    else:
        return Organization.objects.filter(headquater_id=headquater, kind='head').first()


def get_available_users_by_client(unit_id):
    """Получение списка доступных клиенту пользователей"""
    unit_type_id = content_type_ids_for_models(Organization)[0]
    profiles = AccessProfile.objects.filter(unit_type_id=unit_type_id, unit_id=unit_id)
    return profiles.values_list('user', flat=True)


def get_available_users_by_agency(unit_id):
    """Получение списка доступных агентству пользователей"""
    unit_type_id = content_type_ids_for_models(Agency)[0]
    profiles = AccessProfile.objects.filter(unit_type_id=unit_type_id, unit_id=unit_id)
    return profiles.values_list('user', flat=True)

def check_unit(user, unit, permission_roles):
    """ Проверяет конкретный unit """
    unit_type_id = content_type_ids_for_models(type(unit))[0]

    # Получение AccessProfile по всем объектам с учетом иерархии вверх
    profile = AccessProfile.objects.filter(user=user, unit_type_id=unit_type_id,
                                           unit_id__in=get_unit_list_upwards(unit),
                                           headquater=unit.headquater,
                                           role_id__in=permission_roles).first()
    if profile:
        return True
    return False


def check_unit_permission_by_user(user, unit, page_codes=None, action=None):
    # TODO - Не использовать, создан метод check_struct_access_to_page
    """
    unit - объект,
    page_codes - коды зашитые в методы, которые показывают с каких страниц они доступны,
    action - действия
    """
    if user.is_superuser:
        return True

    # Проверка по кодам страниц и действию
    if not page_codes or not action or action not in ACTIONS:
        return False

    # Иерархия по старницам
    pages = Page.objects.filter(code__in=page_codes)
    page_ids = get_page_list_upwards(pages)

    # Получение разрешений по кодам страниц
    permission_roles = Permission.objects.filter(page__id__in=page_ids,
                                                 action=action).values_list('role_id', flat=True)
    if not permission_roles:
        return False

    # Если отдельный объект
    if type(unit) != list:
        return check_unit(user, unit, permission_roles)

    # Если список объектов, проверяем каждый
    for l_unit in unit:
        result = check_unit(user, l_unit, permission_roles)
        if result:
            return True
    return False


def open_role_by_code(code):
    """
    Возвращает объект AccessRole по его коду
    """
    if not code:
        return None
    return AccessRole.objects.filter(code=code).first()
