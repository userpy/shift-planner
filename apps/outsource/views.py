#
# Copyright 2018 ООО «Верме»
#
# Базовые методы отображения страниц и функционал для работы с квотами
#
# Для работы нужен permission/methods.py, который содержит проверку прав доступа;
# rest_framework, outsource/serializers.py, который содержит serializers для методов api
#

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import F, Count
from django.shortcuts import redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse
from django.urls import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from apps.easy_log.shortcuts import *
from copy import copy

import json

from .models import *
from .serializers import *
from .methods import *
from apps.shifts.models import OutsourcingRequest
from apps.claims.models import ClaimRequest
from apps.lib.methods import *
from apps.employees.methods import open_employee
from apps.permission.methods import check_struct_access, check_struct_access_to_page, \
    available_headquarters, available_pages, available_sub_units, available_sel_units
from apps.permission.decorators import check_page_permission_by_user, make_base_context
from apps.violations.methods import make_violations_data, open_violation_level

from django.contrib.auth.models import User
from wfm.settings import LOGIN_URL

from xlsexport.methods import get_report_by_code


def get_user_name(self):
    return f"{self.first_name} {self.last_name} / {self.username}"


User.add_to_class("__str__", get_user_name)


def check_user(request):
    """Ajax авторизация пользователя, запрос с формы логина"""
    if not request.is_ajax():
        return HttpResponseBadRequest()
    username = request.GET.get('username', None)
    password = request.GET.get('password', None)
    data = {'status': 'error'}
    if username:
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            data = {'status': 'ok'}
    return JsonResponse(data)


def user_login(request):
    return render(request, "base/user/login.html")


def user_logout(request):
    logout(request)
    return redirect("/auth/login")


def robots_view(request):
    return render(request, 'robots.txt', content_type='text/plain')


@login_required
def index(request):
    """
    Определение страницы, отображаемой пользователю по умолчанию
    """
    pages = available_pages(request.user)
    # У пользователя нет доступных страниц, переводим на страницу авторизации
    if not pages:
        return redirect(LOGIN_URL)
    target_page = pages.first()
    cookie_page = request.COOKIES.get('page_code')
    if cookie_page:
        target_page = pages.filter(code=cookie_page).first() or target_page
    # Переводим на первую страницу
    return redirect(reverse(target_page.code))


@login_required
@make_base_context
def no_page(request, **context):
    # TODO счетчики
    context.update({"claim_count": 0, "request_count": 0})
    return render(request, "base/no_page.html", context)


@login_required
@make_base_context
def no_access(request, **context):
    # TODO счетчики
    context.update({"claim_count": 0, "request_count": 0})
    return render(request, "base/no_access.html", context)


@login_required
@api_view(['GET'])
def api_get_selector_data_old(request):
    """    Получение значений для селектора 'Выбор организации'  """
    # TODO deprecated
    current_user = request.user
    # Параметр запроса 'party' - категория интерфейса, возможные значения:
    # - agency - Аутсорсинговое агентство,
    # - promo - Агентство-промоутер,
    # - client - Клиент
    party = request.GET.get('party', None)
    if party not in ['agency', 'promo', 'broker', 'client']:
        return HttpResponseBadRequest("Unknown: party")

    # Параметр запроса 'parent', родительская организация, возможные значения:
    headquarter, unit = open_orgunit(request.GET.get('parent', None))
    # Выводим список доступных пользователю клиентов
    if not headquarter:
        headquaters_lst = available_headquarters(current_user, party)
        headquaters = CompanySelSerializer(headquaters_lst, many=True).data
        return Response(headquaters)

    # Проверка прав доступа
    units = available_sub_units(current_user, headquarter, unit)
    if not units or not units.exists():
        return HttpResponseBadRequest("AccessDenied")

    # Выгружаем данные по нижестоящему уровню
    units_data = []
    if (headquarter.party == 'client'):
        units_data = OrganizationSelSerializer(units, many=True).data
    else:
        units_data = AgencySelSerializer(units, many=True).data
    return Response(units_data)


@login_required
@api_view(['GET'])
def api_get_selector_data(request):
    """    Получение значений для селектора 'Выбор организации'  """
    current_user = request.user
    # Параметр запроса 'party' - категория интерфейса, возможные значения:
    # - agency - Аутсорсинговое агентство,
    # - promo - Агентство-промоутер,
    # - client - Клиент
    party = request.GET.get('party', None)
    if party not in ['agency', 'promo', 'broker', 'client']:
        return HttpResponseBadRequest("Unknown: party")

    # Проверка прав доступа
    headquarter_units, units = available_sel_units(current_user, party)
    if not units or not units.exists():
        return HttpResponseBadRequest("AccessDenied")

    units_data = list()
    units_data.extend(CompanySelSerializer(headquarter_units, many=True).data)

    if party == 'client':
        units_data.extend(OrganizationSelSerializer(units, many=True).data)
    else:
        units_data.extend(AgencySelSerializer(units, many=True).data)
    return Response(units_data)


@login_required
@api_view(['GET'])
def api_check_selected_orgunit(request):
    """ Проверка прав доступа текущего пользователя на выбранную орг. единицу """
    current_user = request.user
    # Выполняем поиск объекта выбранной орг. единицы
    headquarter, unit = open_orgunit(request.GET.get('orgunit_id', None))
    if not headquarter:
        return Response({"result": "fail"})
    # Определяем, есть ли у текущего пользователя права доступа на выбранный объект
    if not check_struct_access(current_user, headquarter, unit):
        return Response({"result": "fail"})
    # Возвращаем положительный результат
    return Response({"result": "ok"})


@login_required
@api_view(['GET'])
def api_get_agency_user_counters(request):
    """ Получение количества открытых претензий и не рассмаотренных заявок на аутсорсинг """
    current_user = request.user
    # Выполняем поиск объекта выбранной орг. единицы
    headquarter, unit = open_orgunit(request.GET.get('orgunit_id', None))
    if not headquarter:
        return HttpResponseBadRequest("Unknown: orgunit_id")
    # Определяем, есть ли у текущего п ользователя права доступа на выбранный объект
    elif not check_struct_access(current_user, headquarter, unit):
        return HttpResponseBadRequest("AccessDenied")

    # Определение счетчиков
    requests = OutsourcingRequest.objects.filter(state='accepted')
    claims = ClaimRequest.objects.filter(status__code='wait')
    # Для клиентов
    if headquarter.party == 'client':
        if unit:
            requests = requests.filter(headquater=headquarter, organization=unit)
            claims = claims.filter(headquater=headquarter, organization=unit)
        else:
            requests = requests.filter(headquater=headquarter)
            claims = claims.filter(headquater=headquarter)
    # Для агентств
    else:
        if unit:
            requests = requests.filter(agency=unit)
            claims = claims.filter(agency=unit)
        else:
            agency_ids = Agency.objects.filter(headquater=headquarter).values_list('id', flat=True)
            requests = requests.filter(agency_id__in=agency_ids)
            claims = claims.filter(agency_id__in=agency_ids)

    # Формируем значения счетчтиков
    requests_count = requests.count()
    if requests_count > 9:
        requests_count = '9+'
    claims_count = claims.count()
    if claims_count > 9:
        claims_count = '9+'
    return Response({"request_count": requests_count, "claim_count": claims_count})


""" ******************************* ДОЛЖНОСТИ ********************************** """


@login_required
@api_view(['GET'])
def api_jobs(request):
    """Получение текущих функций агентства"""
    # Определяем агентство
    agency = open_agency(request.GET.get('agency_id', None))
    if not agency:
        employee = open_employee(request.GET.get('agency_employee_id', None))
        agency = employee.agency
    if not agency:
        return make_error_response('Undefined: agency_id / agency_employee_id')
    # Формируем список функций агентства
    return Response(JobSerializer(agency.jobs, many=True).data)


""" ******************************* КВОТЫ ********************************** """


@login_required
@check_page_permission_by_user
def hq_quotas_list(request, **context):
    """Список квот клиента"""
    return render(request, "outsource/hq_quotas_list.html", context)


@login_required
@check_page_permission_by_user
def hq_quotas_volume_list(request, **context):
    """Список ограничений квот клиента"""
    return render(request, "outsource/hq_quotas_volume_list.html", context)


@login_required
@api_view(['GET'])
def api_quotas_list(request):
    """
    API-endpoint для получения списка квотб принимает параметры:
    - headquater_id - ID компании клиента (обязательный параметр)
    - promo_id - ID агентства (фильтр, опциональный)
    - area_id - ID категории товара (фильтра, опциональный)
    - organization_id - ID магазина (Фильтр, опциональный)
    возвращает список квот, на основе переданных параметров
    """
    page_codes = ['hq_quotas_list']
    current_user = request.user

    """Определяем орг. единицу"""
    unit_headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    if not unit_headquarter:
        return make_error_response('Undefined: orgunit')

    """ Проверка прав доступа """
    if not check_struct_access_to_page(current_user, unit_headquarter, unit, page_codes, 'read'):
        return make_error_response('AccessDenied')

    """Получаем organization_id из запроса и фильтруем queryset на основе organization"""
    organization = open_organization(request.GET.get('organization_id', None))

    """Получаем promo_id из запроса и фильтруем queryset на основе promo"""
    promo = open_headquarter(request.GET.get('promo_id', None))

    """Получаем area_id из запроса и фильтруем queryset на основе store_area"""
    store_area = open_storearea(request.GET.get('area_id', None))

    """Получаем дату из запроса"""
    date = request.GET.get('month', None)

    """Определяем нарушения"""
    try:
        violations = json.loads(request.GET.get('violation_ids'))
    except:
        violations = []

    """Формирование queryset для запроса"""
    query_set = make_quotas_queryset(unit_headquarter, unit, date)

    """Копия базового запроса для фильтров"""
    filter_query_set = query_set

    """Ограничиваем запрос по промо агентству"""
    if promo:
        query_set = query_set.filter(promo=promo)

    """Ограничиваем запрос по магазину"""
    if organization:
        query_set = query_set.filter(store=organization)

    """Ограничиваем запрос по зоне магазина"""
    if store_area:
        query_set = query_set.filter(area=store_area)

    """Фильтры"""
    # Список магазинов - формируем полный список, т.к. иначе не будет работать выбор в окне добавления новой квоты
    organization_list = Organization.objects.filter(headquater=unit_headquarter, kind='store')
    if unit:
        organization_list = organization_list.filter(Q(id=unit.id) | Q(parent_id=unit.id))
    organization_list = organization_list.order_by('name').annotate(text=F('name')).values('id', 'text')
    area_list = filter_query_set.order_by('area_id').distinct('area_id').values('area_id', 'area__name'). \
        annotate(id=F('area_id'), text=F('area__name')).values('id', 'text')
    promo_list = filter_query_set.order_by('promo_id').distinct('promo_id').values('promo_id', 'promo__name'). \
        annotate(id=F('promo_id'), text=F('promo__name')).values('id', 'text')

    """Сортировка"""
    sort_fields = ['store__parent__name', 'store__name', 'area__name', 'value', 'value_ext']
    query_set = make_sort(query_set, sort_fields, request.GET.get(u'sort[field]', None),
                          request.GET.get(u'sort[sort]', 'desc'))

    """Фильтрация по нарушениям"""
    if violations:
        for violation_id in violations:
            violation = open_violation_level(violation_id)
            if violation:
                query_set = violation.check_queryset(query_set, date)

    # Выгрузка в Excel
    export = request.GET.get('xlsexport', None)
    if export:
        return get_report_by_code('quota', query_set)

    """Пагинация"""
    query_set, meta = make_pagination(
        query_set,
        request.GET.get('pagination[page]', 1),
        request.GET.get('pagination[perpage]', 10)
    )

    for quota in query_set:
        quota.max_value = quota.max_value(date)
        quota.free_value = quota.free_value(date)
        quota.is_active = quota.check_if_active(date)
        quota.shifts_count = quota.shifts_count(date)
        quota.open_shifts_count = quota.open_shifts_count(date)

    # Формируем ответное сообщение
    ref_data = dict()
    ref_data['meta'] = meta
    ref_data['data'] = QuotaReadSerializer(query_set, many=True).data
    ref_data['promo_list'] = list(promo_list)
    ref_data['organization_list'] = list(organization_list)
    ref_data['area_list'] = list(area_list)
    ref_data['violations_list'] = make_violations_data(page_codes, unit_headquarter.party)

    return Response(ref_data)


@login_required
@api_view(['GET'])
def api_get_quota_areas_promos(request):
    """
    API endpoint для получения доступных зон магазинов и промоутеров
    """
    page_codes = ['hq_quotas_list']

    # Список компаний-промоутеров
    promo_set = Headquater.objects.filter(party__in=['promo', 'broker'])
    promo_list = HeadquaterSelSerializer(promo_set, many=True).data

    # Список зон магазина
    area_set = StoreArea.objects.all()
    area_list = StoreAreaSelSerializer(area_set, many=True).data

    # Формируем ответ
    return Response({"area_list": area_list, "promo_list": promo_list})


@login_required
@api_view(['GET', 'POST', 'DELETE'])
def api_quota(request):
    """
    API endpoint, работает в следующих двух режимах:
    - GET - вывод информации о квоте
    - POST - создание / редактирование одной или нескольких квот
    - DELETE - удаление квоты
    """
    current_user = request.user
    page_codes = ['hq_quotas_list']

    # GET - Получение данных по выбранной квоте
    if request.method == 'GET':
        # Поиск объекта квоты
        quota = open_quota(request.GET.get('quota_id', None))
        if not quota:
            return HttpResponseBadRequest("Undefined: quota_id")
        # ПРОВЕРКА ПРАВ ДОСТУПА
        if not check_struct_access_to_page(current_user, quota.promo, None, page_codes, 'read'):
            return HttpResponseBadRequest("AccessDenied")
        # Формируем ответное сообщение
        return Response({"quota": QuotaReadSerializer(quota, many=False).data})

    # POST - Создание, редактирование
    elif request.method == 'POST':
        # Проверка переданных параметров
        serializer = QuotaWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # ПРОВЕРКА ПРАВ ДОСТУП
        store = serializer.validated_data['store']
        if not check_struct_access_to_page(current_user, store.headquater, store, page_codes, "write"):
            return make_error_response('AccessDenied')

        # РЕДАКТИРОВАНИЕ
        instance = open_quota(request.data.get('quota_id', None))
        previous_instance = copy(instance)
        if instance:
            # Режим работы: apply - изменение, check - проверка возможности
            mode = request.data.get('mode', None)
            if not mode:
                return make_error_response('Undefined: mode')
            # Применение изменений
            if mode == 'apply':
                instance = serializer.update(instance, serializer.validated_data, current_user)
                instance = open_quota(instance.id)
                instance_diff = instance.get_diff(previous_instance)
                log_handler = log_quota_edit
                log_handler(user_id=request.user.id,
                            entity_id=instance.id,
                            headquarter=instance.headquarter_id,
                            organization=instance.store_id,
                            promo=instance.promo_id,
                            start=instance.start,
                            end=instance.end,
                            source_info=None,
                            diff=instance_diff,
                            store_area=instance.area.name,
                            value_total=int(instance.value) + int(instance.value_ext)
                            )
                return Response('Successfully updated', status=status.HTTP_202_ACCEPTED)
            # Проверка
            else:
                # Получаем список связанных смен
                value = serializer.validated_data['value'] + serializer.validated_data['value_ext']
                if value < instance.value_total:
                    result_count = get_quota_related_shifts(instance, value + 1).count()
                else:
                    result_count = 0
                return Response({'result': result_count}, status=status.HTTP_200_OK)
        # СОЗДАНИЕ
        else:
            quota = serializer.save()
            # # Обновление QuotaInfo
            # from apps.shifts.methods import recalc_shifts_quota_info
            # quota_shifts = get_quota_related_shifts(quota)
            # recalc_shifts_quota_info(quota_shifts)
            log_handler = log_quota_new
            instance_diff = {}
            log_handler(user_id=request.user.id,
                        entity_id=quota.id,
                        headquarter=quota.headquarter_id,
                        promo=quota.promo_id,
                        organization=quota.store_id,
                        start=quota.start,
                        end=quota.end,
                        source_info=None,
                        diff=instance_diff,
                        store_area=quota.area.name,
                        value_total=int(quota.value) + int(quota.value_ext)
                        )
            return Response('Successfully created', status=status.HTTP_201_CREATED)

    # DELETE - Удаление квот
    elif request.method == 'DELETE':
        # Список удаляемых квот
        quotas_list = json.loads(request.data['quota_ids']) if 'quota_ids' in request.data else []
        # Режиме работы: apply - удаление, chekc - проверка возможности
        mode = request.data.get('mode', None)
        if not mode:
            return make_error_response('Undefined: mode')

        # Удаление квот из переданного списка
        result_count = 0
        for quota_id in quotas_list:
            quota = open_quota(quota_id)
            if not quota:
                continue
            # Проверка прав доступа
            if not check_struct_access_to_page(current_user, quota.promo, None, page_codes, "write"):
                return make_error_response('AccessDenied')
            # Удаляем квоту
            if mode == 'apply':
                log_handler = log_quota_del
                instance_diff = {}
                log_handler(user_id=request.user.id,
                            entity_id=quota.id,
                            headquarter=quota.headquarter_id,
                            promo=quota.promo_id,
                            organization=quota.store_id,
                            start=quota.start,
                            end=quota.end,
                            source_info=None,
                            diff=instance_diff,
                            store_area=quota.area.name,
                            value_total=int(quota.value) + int(quota.value_ext)
                            )
                remove_quota(quota, request.user.id)
                result_count += 1
            # Подсчитываем количество смен, на которые действует квота
            else:
                result_count += get_quota_related_shifts(quota).count()

        # Формируем ответ
        if mode == 'apply':
            return Response(f'Successfully deleted: {result_count}', status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'result': result_count}, status=status.HTTP_200_OK)

    # Неизвестный метод
    return make_error_response('UnknownError')


@login_required
@api_view(['GET'])
def api_quotas_volume_list(request):
    """
    API-endpoint для получения списка ограничения принимает параметры:
    - area_id - ID категории товара (фильтра, опциональный)
    - organization_id - ID магазина (Фильтр, опциональный)
    возвращает список ограничений квот (QuotaVolume), на основе переданных параметров
    """
    page_codes = ['hq_quotas_volume_list']
    current_user = request.user

    """Определяем орг. единицу"""
    unit_headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    if not unit_headquarter:
        return make_error_response('Undefined: orgunit')

    """ Проверка прав доступа """
    if not check_struct_access_to_page(current_user, unit_headquarter, unit, page_codes, 'read'):
        return make_error_response('AccessDenied')

    """Получаем organization_id из запроса и фильтруем queryset на основе organization"""
    organization = open_organization(request.GET.get('organization_id', None))

    """Получаем area_id из запроса и фильтруем queryset на основе store_area"""
    store_area = open_storearea(request.GET.get('area_id', None))

    """Получаем дату из запроса"""
    date = request.GET.get('month', None)

    """Формирование queryset для запроса"""
    query_set = make_quotas_volume_queryset(unit_headquarter, unit, date)

    """Копия базового запроса для фильтров"""
    filter_query_set = query_set

    """Ограничиваем запрос по магазину"""
    if organization:
        query_set = query_set.filter(store=organization)

    """Ограничиваем запрос по зоне магазина"""
    if store_area:
        query_set = query_set.filter(area=store_area)

    """Фильтры"""
    # Список магазинов - формируем полный список, т.к. иначе не будет работать выбор в окне добавления новой квоты
    organization_list = Organization.objects.filter(headquater=unit_headquarter, kind='store')
    if unit:
        organization_list = organization_list.filter(Q(id=unit.id) | Q(parent_id=unit.id))
    organization_list = organization_list.order_by('name').annotate(text=F('name')).values('id', 'text')
    area_list = filter_query_set.order_by('area_id').distinct('area_id').values('area_id', 'area__name'). \
        annotate(id=F('area_id'), text=F('area__name')).values('id', 'text')

    """Сортировка"""
    sort_fields = ['store__parent__name', 'store__name', 'area__name', 'value']
    query_set = make_sort(query_set, sort_fields, request.GET.get(u'sort[field]', None),
                          request.GET.get(u'sort[sort]', 'desc'))

    # Выгрузка в Excel
    export = request.GET.get('xlsexport', None)
    if export:
        return get_report_by_code('quota_volume', query_set)

    """Пагинация"""
    query_set, meta = make_pagination(
        query_set,
        request.GET.get('pagination[page]', 1),
        request.GET.get('pagination[perpage]', 10)
    )

    # Формируем ответное сообщение
    ref_data = dict()
    ref_data['meta'] = meta
    ref_data['data'] = QuotaVolumeReadSerializer(query_set, many=True).data
    ref_data['organization_list'] = list(organization_list)
    ref_data['area_list'] = list(area_list)

    return Response(ref_data)


@login_required
@api_view(['GET', 'POST', 'DELETE'])
def api_quota_volume(request):
    """
    API endpoint, работает в следующих двух режимах:
    - GET - вывод информации о ограничении квоты
    - POST - создание / редактирование одной или нескольких ограничений квот
    - DELETE - удаление ограничения квоты
    """
    current_user = request.user
    page_codes = ['hq_quotas_volume_list']

    # GET - Получение данных по выбранной квоте
    if request.method == 'GET':
        # Поиск объекта квоты
        quota_volume = open_quota_volume(request.GET.get('quota_volume_id', None))
        if not quota_volume:
            return HttpResponseBadRequest("Undefined: quota_volume_id")
        # ПРОВЕРКА ПРАВ ДОСТУПА
        if not check_struct_access_to_page(current_user, quota_volume.store.headquater, quota_volume.store, page_codes,
                                           'read'):
            return HttpResponseBadRequest("AccessDenied")
        # Формируем ответное сообщение
        return Response({"quota": QuotaVolume(quota_volume, many=False).data})

    # POST - Создание, редактирование
    elif request.method == 'POST':
        # Проверка переданных параметров
        serializer = QuotaVolumeWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # ПРОВЕРКА ПРАВ ДОСТУП
        store = serializer.validated_data['store']
        if not check_struct_access_to_page(current_user, store.headquater, store, page_codes, "write"):
            return make_error_response('AccessDenied')

        # РЕДАКТИРОВАНИЕ
        instance = open_quota_volume(request.data.get('quota_volume_id', None))
        previous_instance = copy(instance)
        if instance:
            # Режим работы: apply - изменение, check - проверка возможности
            mode = request.data.get('mode', None)
            if not mode:
                return make_error_response('Undefined: mode')
            # Применение изменений
            if mode == 'apply':
                instance = serializer.update(instance, serializer.validated_data, current_user)
                instance = open_quota_volume(instance.id)
                instance_diff = instance.get_diff(previous_instance)
                log_handler = log_quota_volume_edit
                log_handler(user_id=request.user.id,
                            entity_id=instance.id,
                            headquarter=instance.store.headquater_id,
                            organization=instance.store_id,
                            start=instance.start,
                            end=instance.end,
                            source_info=None,
                            diff=instance_diff,
                            store_area=instance.area.name
                            )
                return Response('Successfully updated', status=status.HTTP_202_ACCEPTED)
            # Проверка
            else:
                # Получаем список связанных смен
                value = serializer.validated_data['value']
                if value < instance.value:
                    # TODO валидация предупреждения
                    result_count = get_quota_volume_related_quotas(instance).count()
                else:
                    result_count = 0
                return Response({'result': result_count}, status=status.HTTP_200_OK)
        # СОЗДАНИЕ
        else:
            quota_volume = serializer.save()
            log_handler = log_quota_volume_new
            instance_diff = {}
            log_handler(user_id=request.user.id,
                        entity_id=quota_volume.id,
                        headquarter=quota_volume.store.headquater_id,
                        organization=quota_volume.store_id,
                        start=quota_volume.start,
                        end=quota_volume.end,
                        source_info=None,
                        diff=instance_diff,
                        store_area=quota_volume.area.name
                        )
            return Response('Successfully created', status=status.HTTP_201_CREATED)

    # DELETE - Удаление квот
    elif request.method == 'DELETE':
        # Список удаляемых ограничений квот
        quotas_volume_list = json.loads(request.data['quota_volume_ids']) if 'quota_volume_ids' in request.data else []
        # Режиме работы: apply - удаление, check - проверка возможности
        mode = request.data.get('mode', None)
        if not mode:
            return make_error_response('Undefined: mode')

        # Удаление ограничений квот из переданного списка
        result_count = 0
        for quota_volume_id in quotas_volume_list:
            quota_volume = open_quota_volume(quota_volume_id)
            if not quota_volume:
                continue
            # Проверка прав доступа
            if not check_struct_access_to_page(current_user, quota_volume.store.headquater, quota_volume.store,
                                               page_codes, "write"):
                return make_error_response('AccessDenied')
            # Удаляем квоту
            if mode == 'apply':
                log_handler = log_quota_volume_del
                instance_diff = {}
                log_handler(user_id=request.user.id,
                            entity_id=quota_volume.id,
                            headquarter=quota_volume.store.headquater_id,
                            organization=quota_volume.store_id,
                            start=quota_volume.start,
                            end=quota_volume.end,
                            source_info=None,
                            diff=instance_diff,
                            store_area=quota_volume.area.name
                            )
                remove_quota_volume(quota_volume)
                result_count += 1
            # Подсчитываем количество квот, на которые действует ограничение квоты
            else:
                result_count += get_quota_volume_related_quotas(quota_volume).count()

        # Формируем ответ
        if mode == 'apply':
            return Response(f'Successfully deleted: {result_count}', status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'result': result_count}, status=status.HTTP_200_OK)

    # Неизвестный метод
    return make_error_response('UnknownError')


class ApiAgencyInfoView(APIView, ):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        print('ApiAgencyInfoView -....')
        serializer = ApiAgencyInfoRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['employee_id']:
            employee = open_employee(serializer.validated_data['employee_id'])
            if employee:
                agency = employee.agency
            else:
                agency = None
        else:
            agency = open_agency(serializer.validated_data['agency_id'])
        if not agency:
            raise serializers.ValidationError({'non_field_errors': 'Агентство не найдено.'})
        print('Агенства',agency.__dict__)
        return render(request, 'outsource/agencyinfo.html', {'agency':agency})
        print(agency,'+++')
        return Response(AgencyInfoSerializer(agency, many=False).data)
