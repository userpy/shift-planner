#
# Copyright 2018 ООО «Верме»
#
# Файл представлений заявок и смен
#
# Для работы нужен permission/methods.py, который содержит проверку прав доступа;
# rest_framework, outsource/serializers.py, который содержит serializers для методов api
#

from operator import itemgetter
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, F, Q, Max
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone, dateparse
from datetime import datetime, date, timedelta
import json
import calendar
from copy import copy

from django.db.models.functions import Concat
from django.db.models import F, Value, CharField

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from apps.lib.utils import current_utc_offset
from apps.lib.methods import *

from .models import *
from .serializers import *
from .methods import *
from apps.employees.serializers import AgencyEmployeeSerializer, AgencyEmployeeListSerializer
from apps.violations.models import ViolationRuleItem
from apps.violations.methods import check_violation_rules_exists_by_date, check_violation_rules_by_date
from apps.employees.methods import open_employee, get_shift_violation_employee_ids, get_period_violation_employee_ids, \
    make_search
from apps.notifications.methods import make_notify_data
from apps.outsource.models import Agency, Organization, Headquater, Quota, StoreArea, OrgLink
from apps.outsource.methods import get_unit_list_downwards, open_orgunit, open_headquarter, open_agency, \
    open_organization, open_storearea, open_quota, open_job
from apps.permission.decorators import check_page_permission_by_user
from apps.permission.methods import get_client_base_org, check_unit_permission_by_user, check_struct_access_to_page
from xlsexport.methods import get_report_by_code
from apps.easy_log.shortcuts import *
from wfm import settings
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from distutils.util import strtobool

""" ******************************* СПИСОК ЗАПРОСОВ НА АУТСОРСИНГ ********************************** """


@login_required
@check_page_permission_by_user
def requests_list(request, **context):
    """Страница со списком запросов на аутсосринг для менеджера агентства"""
    # TODO счетчики
    context.update({"claim_count": 0, "request_count": 0})
    return render(request, "shifts/requests_list.html", context)


@login_required
@check_page_permission_by_user
def hq_requests_list(request, **context):
    """Страница со списком запросов на аутсосринг для менеджера клиента по работе с агентствами"""
    return render(request, "shifts/hq_requests_list.html", context)


@login_required
def get_outsourcing_requests(request):
    # TODO переименовать метод на api_outsourcing_requests
    """ API endpoint для получения списка заявок на аутсосринг  """
    page_codes = ['requests_list', 'hq_requests_list']
    current_user = request.user

    """Определяем орг. единицу"""
    unit_headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    if not unit_headquarter:
        return make_error_response('Undefined: orgunit')

    """ Проверка прав доступа """
    if not check_struct_access_to_page(current_user, unit_headquarter, unit, page_codes, 'read'):
        return make_error_response('AccessDenied')

    """Получаем agency_id из запроса и фильтруем queryset на основе agency"""
    agency = open_agency(request.GET.get('agency_id', None))

    """Получаем headquater_id из запроса и фильтруем queryset на основе agency"""
    headquarter = open_headquarter(request.GET.get('headquater_id', None))

    """Получаем organization_id из запроса и фильтруем queryset на основе organization"""
    organization = open_organization(request.GET.get('organization_id', None))

    """Получаем дату из запроса"""
    date = request.GET.get('date', None)
    if not date:
        date = request.GET.get('month', None)

    """Формирование queryset для запроса"""
    query_set = make_requests_queryset(unit_headquarter, unit, date)

    """Копия базового запроса для фильтров"""
    filter_query_set = query_set

    """Ограничиваем запрос по клиенту"""
    if headquarter:
        query_set = query_set.filter(headquater=headquarter)

    """Ограничиваем запрос по агентству"""
    if agency:
        query_set = query_set.filter(agency=agency)

    """Ограничиваем запрос по организации"""
    if organization:
        query_set = query_set.filter(organization=organization)

    """Ограничиваем по выбранному статусу заявки"""
    state = request.GET.get('status', 'all')
    if state in ('accepted', 'ready'):
        query_set = query_set.filter(state=state)

    """Фильтры"""
    agency_list = filter_query_set.order_by('agency_id').distinct('agency_id').values('agency_id', 'agency__name'). \
        annotate(id=F('agency_id'), text=F('agency__name')).values('id', 'text')
    organization_list = filter_query_set.select_related('organization').order_by('organization_id'). \
        distinct('organization_id').values_list('organization_id', 'organization__name'). \
        annotate(id=F('organization_id'), text=F('organization__name')).values('id', 'text')

    """Сортировка"""
    sort_fields = ['state', 'organization__name', 'agency__name']
    query_set = make_sort(query_set, sort_fields, request.GET.get(u'sort[field]', None),
                          request.GET.get(u'sort[sort]', 'desc'))

    """Пагинация"""
    query_set, meta = make_pagination(query_set, request.GET.get('pagination[page]', 1),
                                      request.GET.get('pagination[perpage]', 10))

    """Данные таблицы"""
    ref_data = dict()
    ref_data['meta'] = meta
    ref_data['data'] = OutsourcingRequestExtSerializer(query_set, many=True).data
    ref_data['agency_list'] = list(agency_list)
    ref_data['organization_list'] = list(organization_list)
    return JsonResponse(ref_data)


""" ******************************* ПОДТВЕРЖДЕНИЕ СМЕН ЗАЯВКИ ********************************** """


@login_required
@check_page_permission_by_user
def hq_shifts_confirm(request, **context):
    """
    Отображение содержимого заявки на аутсорсинг в режиме просмотра. Параметры запроса:
    + request_id - ID запроса на аутсосринг
    """
    page_codes = ['hq_shifts_confirm']
    current_user = request.user
    # Проверяем возможность доступа сотрудника к выбранному запросу
    out_request = open_outsourcing_request(request.GET.get('request_id', None))
    if not out_request:
        return redirect(reverse('hq_requests_list'))
    if not check_struct_access_to_page(current_user, out_request.headquater, out_request.organization, page_codes,
                                       'read'):
        return make_error_response("AccessDenied")

    # Сбора данных по заявке
    shifts, jobs, days = collect_request_data(out_request)

    context.update({
        "shifts": json.dumps(shifts),
        "jobs": json.dumps(jobs),
        "days": json.dumps(days),
        "request_id": out_request.id,
        "outsourcing_request": out_request,
        "shifts_count": len(shifts),
        "is_org_select_disabled": True,
    })

    # TODO счетчики
    context.update({"claim_count": 0, "request_count": 0})

    # Отрисовка страницы
    return render(request, "shifts/shifts_confirm.html", context)


def collect_request_data(out_request):
    """
    Вспомогательный метод, возвращает данные для отображения запроса
    """
    shifts = OutsourcingShift.objects.filter(request=out_request)
    data = []  # Список смен
    jobs = []  # Список должностей
    days = []  # Список дней
    for s in shifts:
        shift_day = s.start_date.strftime('%d.%m.%Y')
        data.append({"id": s.id, "state": s.state, "worktime": s.worktime, "start": shift_day,
                     "job_name": s.job.name,
                     "period": timezone.localtime(s.start).strftime('%H:%M') + ' - ' + timezone.localtime(
                         s.end).strftime('%H:%M'),
                     "job_id": s.job.id})
        if ({"job_name": s.job.name, "job_id": s.job.id}) not in jobs:
            jobs.append({"job_name": s.job.name, "job_id": s.job.id})
        if ({"start": shift_day}) not in days:
            days.append({"start": shift_day})
    return data, jobs, days


@login_required
@check_page_permission_by_user
def shifts_confirm(request, **context):
    """
    Отображение содержимого заявки на аутсорсинг в режиме подтверждения. Параметры запроса:
    + request_id - ID запроса на аутсосринг
    """
    page_codes = ['shifts_confirm']
    current_user = request.user
    # Проверяем возможность доступа сотрудника к выбранному запросу
    out_request = open_outsourcing_request(request.GET.get('request_id', None))
    if not out_request:
        return redirect(reverse('requests_list'))
    if not check_struct_access_to_page(current_user, out_request.agency.headquater, out_request.agency, page_codes,
                                       'write'):
        return make_error_response("AccessDenied")

    # Сбора данных по заявке
    shifts, jobs, days = collect_request_data(out_request)

    context.update({
        "shifts": json.dumps(shifts),
        "jobs": json.dumps(jobs),
        "days": json.dumps(days),
        "request_id": out_request.id,
        "outsourcing_request": out_request,
        "shifts_count": len(shifts),
        "is_org_select_disabled": True,
    })

    # TODO счетчики
    context.update({"claim_count": 0, "request_count": 0})

    # Отрисовка страницы
    return render(request, "shifts/shifts_confirm.html", context)


@login_required
@api_view(['GET'])
def api_shifts_confirm(request):
    """
    API для работы с подтверждением смен в заявке. В режиме GET-возвращает график
    """
    current_user = request.user
    page_codes = ['hq_shifts_confirm', 'shifts_confirm']

    party = request.GET.get('party', 'client')

    # Параметр запроса - выбранная орг. единица
    # headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    # if not headquarter:
    #    return make_error_response("Unknown: orgunit")
    # Определяем, есть ли у текущего пользователя права доступа на выбранный объект
    # elif not check_struct_access_to_page(current_user, headquarter, unit, page_codes, "read"):
    #    return make_error_response("AccessDenied")

    # Проверяем возможность доступа сотрудника к выбранному запросу
    out_request = open_outsourcing_request(request.GET.get('request_id', None))
    if not out_request:
        return redirect(reverse('requests_list'))
    if not check_struct_access_to_page(current_user, out_request.agency.headquater, out_request.agency, page_codes,
                                       'write'):
        return make_error_response("AccessDenied")

    export = request.GET.get('xlsexport', None)

    # Подготовка данных по сменам данного запроса
    blocks_data = []
    shifts_data = []
    diff_data = []
    shift_ids = []
    agency_ids = [out_request.agency_id]
    for agency_id in agency_ids:
        agency = open_agency(agency_id)

        # Поиск магазинов клиентов, с которыми работает агентство
        store_ids = [out_request.organization_id]
        if store_ids:
            # Поиск смен
            shifts_list = OutsourcingShift.objects.filter(request=out_request)
            shifts_list = shifts_list.select_related('request', 'job').values('start','start_date',
                                                                              'state',
                                                                              'request__organization_id',
                                                                              'request__organization__name',
                                                                              'job_id',
                                                                              'job__name',
                                                                              'job__color',
                                                                              'job__icon')

            # Получение максимального кол-ва смен из всех дней периода, т.к. в запросе выше нельзя сделать Max
            # от вычисляемого значения
            max_size = dict()
            my_max_size = {}
            for sh in shifts_list:
                my_max_size[(sh['request__organization_id'], sh['job_id'])] = my_max_size.get((sh['request__organization_id'], sh['job_id']), [])
                my_max_size[(sh['request__organization_id'], sh['job_id'])].append(sh['start'].strftime('%Y-%m-%d'))
            # Создание блоков на основе данных того же запроса, чтобы не делать новый
            processed_list = []
            if shifts_list.exists():
                # Добавляем собранную информацию об агентсве и его квотах
                row_data = []
                for row in shifts_list:
                    if (row['request__organization_id'], row['job_id']) in processed_list:
                        continue
                    store_data = {"id": row['request__organization_id'], "name": row['request__organization__name']}
                    area_data = {"id": f"{row['request__organization_id']}_{row['job_id']}", "name": row['job__name'],
                                 "icon": row['job__icon'], "color": row['job__color']}
                    from collections import Counter
                    row_data.append({"organization": store_data, "area": area_data,
                                     "size": max(Counter(my_max_size[(row['request__organization_id'], row['job_id'])]).values())
                                     })
                                     # "size": max_size[(row['request__organization_id'], row['job_id'])]})
                    processed_list.append((row['request__organization_id'], row['job_id']))
                blocks_data.append({"id": agency.id, "name": agency.name, "rows": row_data})

        # Поиск ранее спланированных смен
        shifts_list = OutsourcingShift.objects.filter(request=out_request)

        if shifts_list.exists():
            current_row_index = dict()
            for shift in shifts_list:
                urow_index = current_row_index.get((shift.request.organization_id, shift.job_id, shift.start_date), 0)
                shift.urow_index = urow_index
                current_row_index[(shift.request.organization_id, shift.job_id, shift.start_date)] = urow_index + 1
                if export:
                    shift_ids.append(shift.id)
            shifts_data.extend(OutsourcingShiftReadSerializer(shifts_list, many=True).data)

    # Массив для информации о подтвержденных сменах
    workload = []

    # Начальный и конечный период заявки
    start = out_request.start
    end = out_request.end
    step = timedelta(days=1)

    # Для каждого дня из периода
    while start <= end:
        # Поиск подтвержденных смен на данную дату
        accepted_shifts = OutsourcingShift.objects. \
            filter(state='accept', start_date=start, agency_id=out_request.agency_id). \
            annotate(text=F('job__name')).values('text').order_by(). \
            annotate(total=Count('text')).order_by('text')
        # Если есть смены
        if accepted_shifts:
            # Формируем информацию по дню
            day = dict()
            day[start.isoformat()] = list(accepted_shifts)
            workload.append(day)
        # Сдвигаем дату на следующий день
        start += step

    # Выгрузка в Excel
    if export:
        return get_report_by_code(f'{party}shifts_confirm', OutsourcingShift.objects.filter(id__in=shift_ids))

    # Возвращем полученный результат
    return Response({"blocks": blocks_data, "shifts": shifts_data, "diff": diff_data, "workload": workload})


@login_required
@api_view(['POST'])
def update_request(request):
    """ Подтверждение заявки и входящих в нее смен """
    page_codes = ['shifts_confirm']

    if request.method == 'POST':
        # Поиск и проверка состояния обрабатываемого запроса
        out_request_id = request.data.get('request_id', None)
        try:
            out_request = OutsourcingRequest.objects.get(pk=out_request_id)
            # Проверка прав доступа
            if not check_unit_permission_by_user(request.user, out_request.agency, page_codes, 'read'):
                return make_error_response('AccessDenied')
        except OutsourcingRequest.DoesNotExist:
            return make_error_response('Не найдена заявка с таким id')
        if out_request.state != 'accepted':
            return make_error_response('Некорректный статус заявки')

        # Счетчики количества смен
        accept_total = 0
        reject_total = 0

        g_action = request.data.get('action', None)
        reject_reason = request.data.get('reject_reason', None)

        # Отклонить заявку
        if g_action == 'reject':
            if not reject_reason:
                return make_error_response('Не заполнена причина отклонения заявки')
            with transaction.atomic():
                out_request.state = 'ready'
                out_request.dt_ready = timezone.now()
                out_request.reject_reason = reject_reason
                out_request.save()
                # Все заявки по умолчанию отклоняем
                reject_total = OutsourcingShift.objects.filter(request=out_request_id).exclude(state='delete').update(
                    state='reject')
            # Создаем и отправляем уведомления об отклонении заявки
            make_notify_data(out_request, 'client', 'reject_req_template')
        # Принять заявку
        elif g_action == 'accept':  # update
            with transaction.atomic():
                out_request.state = 'ready'
                out_request.dt_ready = timezone.now()
                out_request.save()
                # Все заявки по умолчанию считаем принятыми, после чего корректируем данными с сервера
                accept_total = OutsourcingShift.objects.filter(request=out_request_id, state='wait').update(
                    state='accept')
                g_shifts = json.loads(request.data.get('shifts', None))
                for response_shift in g_shifts:
                    # Смены в состоянии wait были переведены в accept запросом выше
                    if response_shift['state'] == 'wait':
                        continue
                    # Пропускаем, если смена принадлежит к другой заявке или удалена
                    out_shift = OutsourcingShift.objects.get(pk=response_shift['id'])
                    if out_shift.request != out_request or out_shift.state == 'delete':
                        continue
                    # Меняем состояние смены на заданное пользователем
                    if out_shift.state != response_shift['state']:
                        out_shift.state = response_shift['state']
                        out_shift.save()
                        accept_total -= 1
                        if response_shift['state'] == 'reject':
                            reject_total += 1

                    if reject_total > 0:
                        if not reject_reason:
                            transaction.rollback()
                            return make_error_response('Не заполнена причина отклонения смен заявки')
                        out_request.reject_reason = reject_reason
                        out_request.save(update_fields=['reject_reason'])
            # Создаем и отправляем уведомления о подтверждении заявки
            make_notify_data(out_request, 'client', 'accept_req_template')

        else:
            return make_error_response('Некорректное действие')
        return Response('Successfully updated', status=status.HTTP_200_OK)
    return make_error_response('UnknownError')


@login_required
@api_view(['GET'])
def api_shifts_workload(request):
    """API endpoint для получения количества назначений на дни смены в заявке
    принимает параметры:
    request_id типа int (1)
    возвращает:
    список смен c полем
    "workload": [{"job__name": ,"total": }]
    показывающем сколько есть смен в состоянии accept на этот день с указанными функциями
    """
    page_codes = ['shifts_list']
    if request.method == 'GET':
        # Определяем объект заявки
        request_id = request.GET.get('request_id', None)
        try:
            request_id = int(request_id)
        except:
            return make_error_response("No request_id")
        out_request = get_object_or_404(OutsourcingRequest, id=request_id)

        # Проверка прав доступа
        if not check_unit_permission_by_user(request.user, out_request.agency, page_codes, 'read'):
            return make_error_response("No permission")

        # Словарь ответа
        resp = dict()
        resp['jobs'] = []

        # Массив для информации о подтвержденных сменах
        workload = []

        # Начальный и конечный период заявки
        start = out_request.start
        end = out_request.end
        step = timedelta(days=1)

        # Для каждого дня из периода
        while start <= end:
            # Поиск подтвержденных смен на данную дату
            accepted_shifts = OutsourcingShift.objects. \
                filter(state='accept', start_date=start, agency_id=out_request.agency_id). \
                values('job__name').order_by(). \
                annotate(total=Count('job__name')).order_by('job__name')
            # Если есть смены
            if accepted_shifts:
                # Формируем информацию по дню
                day = dict()
                day['start_date'] = start.isoformat()
                day['workload'] = list(accepted_shifts)
                workload.append(day)

                # Добавляем функцию подтвержденной смены в список функций
                for accepted_shift in accepted_shifts:
                    if accepted_shift['job__name'] not in resp['jobs']:
                        resp['jobs'].append(accepted_shift['job__name'])
            # Сдвигаем дату на следующий день
            start += step
        resp['shifts'] = workload
        return Response(resp)


""" ******************************* СПИСОК СМЕН АУТСОРСЕРОВ ********************************** """


@login_required
@check_page_permission_by_user
def shifts_list(request, **context):
    """Список смен для менеджера аутсорсингового агентства """
    return render(request, "shifts/shifts_list.html", context)


@login_required
@check_page_permission_by_user
def hq_shifts_list(request, **context):
    """Список смен для менеджера клиента по работе с аутсорсинговыми агентствами """
    return render(request, "shifts/hq_shifts_list.html", context)


@login_required
@api_view(['GET'])
def api_shifts_list(request):
    """API endpoint для получения смен на дату и назначения сотрудников
    принимает параметры:
    agency_id типа int (1) и/или headquater_id типа int (1)
    возвращает список заявок, на основе переданных параметров
    """
    page_codes = ['shifts_list', 'hq_shifts_list']
    current_user = request.user

    """Определяем орг. единицу"""
    unit_headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    if not unit_headquarter:
        return make_error_response('Undefined: orgunit')

    """ Проверка прав доступа """
    if not check_struct_access_to_page(current_user, unit_headquarter, unit, page_codes, 'read'):
        return make_error_response('AccessDenied')

    """Получаем agency_id из запроса и фильтруем queryset на основе agency"""
    agency = open_agency(request.GET.get('agency_id', None))

    """Получаем headquater_id из запроса и фильтруем queryset на основе agency"""
    headquarter = open_headquarter(request.GET.get('headquater_id', None))

    """Получаем organization_id из запроса и фильтруем queryset на основе organization"""
    organization = open_organization(request.GET.get('organization_id', None))

    """Получаем дату из запроса"""
    date = request.GET.get('date', None)

    """Формирование queryset для запроса"""
    query_set = make_shifts_queryset(unit_headquarter, unit, date)

    """Копия базового запроса для фильтров"""
    filter_query_set = query_set

    """Ограничиваем запрос по клиенту"""
    if headquarter:
        query_set = query_set.filter(headquater=headquarter)

    """Ограничиваем запрос по агентству"""
    if agency:
        query_set = query_set.filter(agency=agency)

    """Ограничиваем запрос по организации"""
    if organization:
        query_set = query_set.filter(request__organization=organization)

    """Получаем status из запроса и фильтруем queryset на основе status"""
    status = request.GET.get('status', 'all')
    if status == 'assigned':
        query_set = query_set.filter(agency_employee__isnull=False)
    elif status == 'unassigned':
        query_set = query_set.filter(agency_employee__isnull=True)

    """Фильтры"""
    agency_list = filter_query_set.order_by('agency_id').distinct('agency_id').values('agency_id', 'agency__name'). \
        annotate(id=F('agency_id'), text=F('agency__name')).values('id', 'text')
    organization_list = filter_query_set.select_related('request').order_by('request__organization__id'). \
        distinct('request__organization__id'). \
        values('request__organization__id', 'request__organization__name'). \
        annotate(id=F('request__organization__id'), text=F('request__organization__name')).values('id', 'text')

    """Поиск по ФИО, наименованию функции"""
    search = request.GET.get(u'datatable[query][generalSearch]', None)
    if search:
        search_list = search.split(" ")
        for ss in search_list:
            if not ss or len(ss) < 3:
                continue
            query_set = query_set.filter(Q(agency_employee__surname__icontains=ss) |
                                         Q(agency_employee__firstname__icontains=ss) |
                                         Q(agency_employee__patronymic__icontains=ss) |
                                         Q(job__name__icontains=ss))

    query_set = query_set.order_by('start')

    """Пагинация"""
    query_set, meta = make_pagination(query_set, request.GET.get('pagination[page]', 1),
                                      request.GET.get('pagination[perpage]', 10))

    ref_data = dict()
    ref_data['meta'] = meta
    ref_data['data'] = OusourcingShiftSerializer(query_set, many=True).data
    ref_data['agency_list'] = list(agency_list)
    ref_data['organization_list'] = list(organization_list)
    return Response(ref_data)


@login_required
@api_view(['GET'])
def api_shift_violations(request):
    """ Возвращает список нарушений по смене"""
    current_user = request.user
    agency_pages = ['promo_schedule', 'broker_schedule']

    # Смена
    shift = open_promo_shift(request.GET.get('shift_id', None))

    # Сотрудник
    agency_employee = open_employee(request.GET.get('agency_employee_id', None))
    if not shift and not agency_employee:
        return make_error_response('Undefined: agency_employee_id')

    # Начало смены
    start = request.GET.get('start', None)
    if not shift and not start:
        return make_error_response('Undefined: start')

    if start:
        date = dateparse.parse_datetime(request.GET['start']).date()
    else:
        date = None

    # ПРОВЕРКА ПРАВ ДОСТУПА
    if shift and check_struct_access_to_page(current_user, shift.aheadquarter, shift.agency, agency_pages, 'read'):
        if shift and shift.agency_employee:
            return Response(check_violation_rules_by_date(agency_pages, shift.aheadquarter, shift.agency_employee,
                                                          shift.start_date))
        return Response([])
    elif agency_employee and check_struct_access_to_page(current_user, agency_employee.agency.headquater,
                                                         agency_employee.agency, agency_pages, 'read'):
        if agency_employee and date:
            return Response(
                check_violation_rules_by_date(agency_pages, agency_employee.agency.headquater, agency_employee, date))
    else:
        return make_error_response('AccessDenied')


""" График планирования смен аутсорсеров """


@login_required
@check_page_permission_by_user
def outsource_schedule(request, **context):
    """График смен для аутсорсеров"""
    context.update({"current_utc_offset": current_utc_offset()})
    return render(request, "shifts/schedule.html", context)


@login_required
@api_view(['GET', 'POST'])
def api_outsource_schedule(request):
    """
    API для работы с графиком смен аутсорсеров. В режиме GET-возвращает график, в режиме POST вносит изменения
    """
    current_user = request.user
    page_codes = ['outsource_schedule']

    party = request.GET.get('party', 'agency')

    # Параметр запроса - выбранная орг. единица
    headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    if not headquarter:
        return make_error_response("Unknown: orgunit")
    # Определяем, есть ли у текущего пользователя права доступа на выбранный объект
    elif not check_struct_access_to_page(current_user, headquarter, unit, page_codes, "read"):
        return make_error_response("AccessDenied")

    # Параметры запроса - границы рассматриваемого периода
    start_date = request.GET.get('start', None)
    if not start_date:
        return make_error_response("Undefined: start")
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    end_date = request.GET.get('end', None)
    if not end_date:
        return make_error_response("Undefined: end")
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    # Месяц на который рассчитываются квоты
    month = request.GET.get('month', None)
    if month:
        month_start = datetime.datetime.strptime(month, '%Y-%m-%d').date()
        month_max_day = calendar.monthrange(month_start.year, month_start.month)[1]
        month_end = month_start.replace(day=month_max_day)

    export = request.GET.get('xlsexport', None)

    # Подготовка данных по сменам выбранных агентств
    blocks_data = []
    shifts_data = []
    diff_data = []
    shift_ids = []
    agency_ids = get_unit_list_downwards(headquarter, unit, True)
    for agency_id in agency_ids:
        agency = open_agency(agency_id)

        # Поиск магазинов клиентов, с которыми работает агентство
        store_ids = OrgLink.objects.filter(agency=agency).values_list('organization_id', flat=True)
        if store_ids:
            # Поиск смен
            shifts_list = OutsourcingShift.objects.filter(request__state='ready'). \
                filter(Q(agency=agency, request__organization_id__in=store_ids) |
                       Q(agency=agency, request__organization__parent_id__in=store_ids)).filter(state='accept')
            if month:
                shifts_list = shifts_list.filter(Q(start_date__gte=month_start) & Q(start_date__lte=month_end))
            else:
                shifts_list = shifts_list.filter(Q(start_date__gte=start) & Q(start_date__lte=end))

            shifts_list = shifts_list.select_related('request', 'job').values('start_date',
                                                                              'request__organization_id',
                                                                              'request__organization__name',
                                                                              'job_id',
                                                                              'job__name',
                                                                              'job__color',
                                                                              'job__icon'). \
                annotate(dcount=Count('id'))

            # Получение максимального кол-ва смен из всех дней периода, т.к. в запросе выше нельзя сделать Max
            # от вычисляемого значения
            max_size = dict()
            for sh in shifts_list:
                max_size[(sh['request__organization_id'], sh['job_id'])] = max(
                    max_size.get((sh['request__organization_id'], sh['job_id']), 0), sh['dcount'])

            # Создание блоков на основе данных того же запроса, чтобы не делать новый
            processed_list = []
            if shifts_list.exists():
                # Добавляем собранную информацию об агентсве и его квотах
                row_data = []
                for row in shifts_list:
                    if (row['request__organization_id'], row['job_id']) in processed_list:
                        continue
                    store_data = {"id": row['request__organization_id'], "name": row['request__organization__name']}
                    area_data = {"id": f"{row['request__organization_id']}_{row['job_id']}", "name": row['job__name'],
                                 "icon": row['job__icon'], "color": row['job__color']}
                    row_data.append({"organization": store_data, "area": area_data,
                                     "size": max_size[(row['request__organization_id'], row['job_id'])]})
                    processed_list.append((row['request__organization_id'], row['job_id']))
                blocks_data.append({"id": agency.id, "name": agency.name, "rows": row_data})

        # Поиск ранее спланированных смен
        shifts_list = OutsourcingShift.objects.filter(agency=agency).filter(state='accept', request__state='ready')
        shifts_list = shifts_list.filter(start_date__gte=start, start_date__lte=end)

        if shifts_list.exists():
            current_row_index = dict()
            for shift in shifts_list:
                urow_index = current_row_index.get((shift.request.organization_id, shift.job_id, shift.start_date), 0)
                shift.urow_index = urow_index
                current_row_index[(shift.request.organization_id, shift.job_id, shift.start_date)] = urow_index + 1
                if export:
                    shift_ids.append(shift.id)
            shifts_data.extend(OutsourcingShiftReadSerializer(shifts_list, many=True).data)

    # Выгрузка в Excel
    if export:
        return get_report_by_code(f'{party}shift', OutsourcingShift.objects.filter(id__in=shift_ids))

    # Возвращем полученный результат
    return Response({"blocks": blocks_data, "shifts": shifts_data, "diff": diff_data})


@login_required
@api_view(['GET', 'POST'])
def api_shift_employee(request):
    """
    API endpoint, работает в следующих двух режимах:
    - GET - для заданной смены возвращает список подходящих сотрудников
    - POST - меняет сотрудника, назначенного на смену
    """
    current_user = request.user
    page_codes = ['shifts_list']

    # ПОИСК ОБЪЕКТА СМНЫ
    out_shift = None
    if request.method == 'GET':
        out_shift = request.GET.get('shift_id', None)
    elif request.method == 'POST':
        out_shift = request.data['id']
    out_shift = open_outsourcing_shift(out_shift)
    if not out_shift:
        return make_error_response("Undefined: shift_id")

    # ПРОВЕРКА СОСТОЯНИЯ СМЕНЫ:
    # - смена должна быть в состоянии "Подтверждена контрагентом"
    if out_shift.state != 'accept':
        return make_error_response("Error: shift not in accept state")
    # - запрос на аутсорсинг должен быть в состоянии "Обработан"
    if not out_shift.request or out_shift.request.state != 'ready':
        return make_error_response("Error: request not in ready state")
    # - смена не должна относиться к прошлому периоду
    if out_shift.start_date < timezone.now().date():
        return make_error_response("Error: shift in past period")

    # ПРОВЕРКА ПРАВ ДОСТУПА
    if not check_struct_access_to_page(current_user, out_shift.agency.headquater, out_shift.agency, page_codes,
                                       'write'):
        return make_error_response("AccessDenied")

    # GET-метод: возвращает список сотрудников, которых можно назначить на смену
    if request.method == 'GET':
        employees = query_free_employees_for_shift(out_shift)
        serialized = AgencyEmployeeSerializer(employees, many=True)
        return Response(json.dumps(serialized.data))

    # POST-метод: меняем назначенного на смену сотрудника
    elif request.method == 'POST':
        request_data = request.data.copy()
        request_data['agency_employee_id'] = request_data.get('agency_employee_id', '') or request_data.get(
            'employee_id', '')
        # Проверка корректности переданных данных
        serializer = OusourcingShiftSerializer2(data=request_data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Если передан новой сотрудник, то проверяем, действительно ли его можно назначить на смену
        if request_data['agency_employee_id'] != '':
            employee = open_employee(request_data['agency_employee_id'])
            if not employee:
                return make_error_response("Invalid: agency_employee_id")
            if not can_set_employee_to_shft(employee, out_shift):
                return make_error_response("Error: Employee can't be assigned to the shift")

        # Корректируем выбранную смену
        previous_instance = copy(out_shift)
        new_instance = serializer.update(out_shift, request_data)
        out_shift = open_outsourcing_shift(new_instance.id)
        instance_diff = out_shift.get_diff(previous_instance)
        log_handler = log_out_shift_edit
        log_handler(user_id=request.user.id,
                    entity_id=out_shift.id,
                    headquarter=out_shift.headquater_id,
                    aheadquarter=out_shift.agency.headquater_id,
                    organization=out_shift.request.organization_id,
                    agency=out_shift.agency_id,
                    start=out_shift.start,
                    end=out_shift.end,
                    source_info=None,
                    diff=instance_diff,
                    job=out_shift.job.name
                    )
        return Response(OutsourcingShiftReadSerializer([out_shift], many=True).data, status=status.HTTP_201_CREATED)

    # НЕВОЗМОЖНАЯ СИТУАЦИЯ
    return make_error_response("UnknownError")


""" ******************************* ПЛАНИРОВАНИ СМЕН ПРОМОУТЕРОВ ********************************** """


@login_required
@check_page_permission_by_user
def promo_schedule(request, **context):
    """График смен для промоутера"""
    context.update({"current_utc_offset": current_utc_offset()})
    return render(request, "shifts/schedule.html", context)


@login_required
@check_page_permission_by_user
def broker_schedule(request, **context):
    """График смен для кредитных брокеров"""
    context.update({"current_utc_offset": current_utc_offset()})
    return render(request, "shifts/schedule.html", context)


@login_required
@check_page_permission_by_user
def client_schedule(request, **context):
    """График доступности"""
    context.update({"current_utc_offset": current_utc_offset()})
    return render(request, "shifts/schedule.html", context)


from .models import Headquater, Agency, Organization


class ApiClientScheduleView(APIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    page_codes = ['client_schedule']
    headquarter = None
    unit = None

    def get_orgunit(self, orgid, orgtype):
        try:

            if orgtype == 'headquater':
                self.headquarter = Headquater.objects.get(pk=orgid)
            else:
                obj = Agency
                if orgtype != 'agency':
                    obj = Organization
                self.unit = obj.objects.get(pk=orgid)
                self.headquarter = self.unit.headquater
        except (Agency.DoesNotExist, Headquater.DoesNotExist, Organization.DoesNotExist):
            raise ValidationError({'orgunit':'Not valid'})

    def get(self, request):

        serializer = ApiClientScheduleRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        start = serializer.validated_data['start']
        end = serializer.validated_data['end']
        month = serializer.validated_data['month']
        export = serializer.validated_data['export']
        self.get_orgunit(*serializer.validated_data['orgunit'])
        if month:
            month_start = datetime.datetime.strptime(month, '%Y-%m-%d').date()
            month_max_day = calendar.monthrange(month_start.year, month_start.month)[1]
            month_end = month_start.replace(day=month_max_day)
        shifts_data = []
        diff_data = []
        avails_data = []
        shift_ids = []
        blocks_data = []

        if not self.unit or self.unit.kind != 'store':
            raise ValidationError({'non_field_errors':
                'Отображение для выбранного уровня организационной структуры недоступно. Выберите уровень магазин.'})
        if not check_struct_access_to_page(request.user, self.headquarter, self.unit, self.page_codes, "read"):
            return make_error_response("AccessDenied")

        # Получение агентств, работающих с магазином
        agencies_pks = OrgLink.objects.filter(organization=self.unit).order_by('agency_id').distinct('agency_id').values_list('agency_id', flat=True)
        agencies = Agency.objects.filter(id__in=agencies_pks)
        promo_pks = agencies.order_by('headquater_id').distinct('headquater_id').values_list('headquater_id', flat=True)

        if month:
            quotas = Quota.objects.date_filter(month_start, month_end)
        else:
            quotas = Quota.objects.date_filter(start, end)
        quotas = quotas.filter(store=self.unit, promo_id__in=promo_pks).order_by('-start')

        names_quota = []
        row_data = []
        for agency in agencies:

            for quota in quotas:
                # еслит похожая квота более позняя уже есть, или не относится к данному прому
                if str(quota) in names_quota or agency.headquater != quota.promo:
                    continue
                names_quota.append(str(quota))
                row = {
                    'organization': {
                        'id': agency.pk,
                        'name': agency.name,
                    },
                    'area': AreaSerializer(quota.area).data,
                    'size': quota.value_total
                }
                row_data.append(row)
        if len(row_data) > 0:
            blocks_data.append({
                "id": self.unit.id, "name": self.unit.name,
                "rows": row_data})

        shifts_list = PromoShift.objects.select_related().filter(agency_id__in=agencies_pks, organization=self.unit).exclude(state='delete').filter(
            start_date__gte=start, start_date__lte=end, )
        # Поиск доступностей
        avails_list = Availability.objects.filter(agency__in=agencies_pks, start__gte=start, start__lte=end)
        print('ok')
        if shifts_list:
            for shift in shifts_list:
                if export:
                    shift_ids.append(shift.id)

            if len(blocks_data) > 0:
                print(shifts_list.count())
                shifts_data.extend(PromoShiftReadSerializer(shifts_list, many=True).data)
                avails_data.extend(AvailabilityReadSerializer(avails_list, many=True).data)
            else:
                diff_data.extend(PromoShiftReadSerializer(shifts_list, many=True).data)

        if export:
            return get_report_by_code(f'clientshift', PromoShift.objects.filter(id__in=shift_ids))

        # Возвращем полученный результат
        return Response({"blocks": blocks_data, "shifts": shifts_data, "diff": diff_data, "avails": avails_data})


@login_required
@api_view(['GET', 'POST'])
def api_promo_schedule(request):
    """
    API для работы с графиком смен промоутеров. В режиме GET-возвращает график, в режиме POST вносит изменения
    """
    current_user = request.user
    page_codes = ['promo_schedule', 'broker_schedule']

    party = request.GET.get('party', 'promo')

    # Параметр запроса - выбранная орг. единица
    headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    if not headquarter:
        return make_error_response("Unknown: orgunit")
    # Определяем, есть ли у текущего п ользователя права доступа на выбранный объект
    elif not check_struct_access_to_page(current_user, headquarter, unit, page_codes, "read"):
        return make_error_response("AccessDenied")

    # Параметры запроса - границы рассматриваемого периода
    start_date = request.GET.get('start', None)
    if not start_date:
        return make_error_response("Undefined: start")
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    end_date = request.GET.get('end', None)
    if not end_date:
        return make_error_response("Undefined: end")
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    # Месяц на который рассчитываются квоты
    month = request.GET.get('month', None)
    if month:
        month_start = datetime.datetime.strptime(month, '%Y-%m-%d').date()
        month_max_day = calendar.monthrange(month_start.year, month_start.month)[1]
        month_end = month_start.replace(day=month_max_day)

    export = request.GET.get('xlsexport', None)

    # Подготовка данных по квотам выбранных агентств
    blocks_data = []
    shifts_data = []
    diff_data = []
    avails_data = []
    shift_ids = []
    agency_ids = get_unit_list_downwards(headquarter, unit, True)

    for agency_id in agency_ids:
        agency = open_agency(agency_id)
        has_quotas = False

        # Перечень магазинов, работающих с агентством
        store_ids = OrgLink.objects.filter(agency=agency).select_related('organization__parent')
        # Массив для хранения распределения по городам
        cities_dict = {}
        if store_ids:
            # Поиск квот на выбранного промоутера и ранее спланированных смен
            quota_list = Quota.objects.filter(promo=headquarter, store_id__in=store_ids.values_list('organization_id',
                                                                                                    flat=True))
            if month:
                quota_list = quota_list.filter(Q(start__lte=month_start, end__isnull=True) |
                                               Q(start__lte=month_start, end__gte=month_end))
            else:
                quota_list = quota_list.filter(
                    Q(start__lte=start, end__isnull=True) | Q(start__lte=start, end__gte=end))

            quota_list = quota_list.select_related('area', 'store', 'store__parent').order_by('store_id', '-start')
            if quota_list.exists():
                for quota in quota_list:
                    # Проверка, что квота является активной
                    if not quota.check_if_active(month):
                        continue
                    #
                    if quota.store.kind == 'store' and quota.store.parent.kind == 'city':
                        if quota.store.parent.id not in cities_dict:
                            cities_dict.update({quota.store.parent.id: {"id": f"{agency.id}_{quota.store.parent.id}",
                                                                        "name": f"{agency.name} / {quota.store.parent.name}",
                                                                        "rows": []}})

                        store_data = {"id": quota.store.id, "name": quota.store.name}
                        area_data = {"id": quota.area.id, "name": quota.area.name, "color": quota.area.color,
                                     "icon": quota.area.icon}

                        cities_dict[quota.store.parent.id]["rows"].append(
                            {"organization": store_data, "area": area_data, "size": quota.value_total})

                blocks_data.extend([v for k, v in cities_dict.items()])
                has_quotas = True

        # Поиск ранее спланированных смен
        shifts_list = PromoShift.objects.filter(agency=agency).exclude(state='delete').\
            select_related('organization__parent').\
            annotate(agency_city=Concat(F('agency_id'), Value('_'), F('organization__parent__id'), output_field=CharField()))

        shifts_list = shifts_list.filter(start_date__gte=start, start_date__lte=end)

        # Поиск доступностей
        avails_list = Availability.objects.filter(agency=agency, start__gte=start, start__lte=end). \
            select_related('organization__parent'). \
            annotate(agency_city=Concat(F('agency_id'), Value('_'), F('organization__parent__id'), output_field=CharField()))

        if shifts_list.exists():
            if party == 'promo':
                # Сотрудники с нарушениями по мед. книжке
                violation_employee_ids = get_shift_violation_employee_ids(shifts_list)
                violation_item = ViolationRuleItem.objects.filter(rule__code='medical', severity='high').order_by(
                    'value_from').first()
            for shift in shifts_list:
                if party == 'promo':
                    days_value = violation_item.value_to if violation_item else 0
                    if shift.agency_employee_id and shift.start_date + timedelta(days=days_value) > \
                            violation_employee_ids[shift.agency_employee_id]:
                        shift.has_violations = True
                if export:
                    shift_ids.append(shift.id)

            if has_quotas:
                shifts_data.extend(PromoShiftReadSerializer(shifts_list, many=True).data)
            else:
                diff_data.extend(PromoShiftReadSerializer(shifts_list, many=True).data)
        if has_quotas:
            avails_data.extend(AvailabilityReadSerializer(avails_list, many=True).data)

    # Выгрузка в Excel
    if export:
        return get_report_by_code(f'{party}shift', PromoShift.objects.filter(id__in=shift_ids))

    # Возвращем полученный результат
    return Response({"blocks": blocks_data, "shifts": shifts_data, "diff": diff_data, "avails": avails_data})


@login_required
@api_view(['GET'])
def api_client_schedule(request):
    """
    API для работы с графиком доступностей. В режиме GET-возвращает график
    """
    current_user = request.user
    page_codes = ['client_schedule']

    party = request.GET.get('party', 'client')
    mode = request.GET.get('mode', 'promo')

    # Параметр запроса - выбранная орг. единица
    headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    if not headquarter:
        return make_error_response("Unknown: orgunit")
    # Определяем, есть ли у текущего п ользователя права доступа на выбранный объект
    elif not check_struct_access_to_page(current_user, headquarter, unit, page_codes, "read"):
        return make_error_response("AccessDenied")
    if not unit or unit.kind != 'store':
        raise ValidationError({'non_field_errors':
                                   'Отображение для выбранного уровня организационной структуры недоступно. '
                                   'Выберите уровень магазин.'})
    # Параметры запроса - границы рассматриваемого периода
    start_date = request.GET.get('start', None)
    if not start_date:
        return make_error_response("Undefined: start")
    start = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()

    end_date = request.GET.get('end', None)
    if not end_date:
        return make_error_response("Undefined: end")
    end = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    # Месяц на который рассчитываются квоты
    month = request.GET.get('month', None)
    if month:
        month_start = datetime.datetime.strptime(month, '%Y-%m-%d').date()
        month_max_day = calendar.monthrange(month_start.year, month_start.month)[1]
        month_end = month_start.replace(day=month_max_day)

    export = request.GET.get('xlsexport', None)

    # Подготовка данных по квотам выбранных агентств
    blocks_data = []
    shifts_data = []
    diff_data = []
    avails_data = []
    shift_ids = []
    organization_ids = get_unit_list_downwards(headquarter, unit, True)
    for organization_id in organization_ids:
        organization = open_organization(organization_id)
        has_quotas = False

        if mode == 'outsource':
            agency_ids = OrgLink.objects.filter(Q(organization=organization) | Q(organization__parent=organization)). \
                filter(aheadquarter__party='agency'). \
                order_by('agency_id').distinct('agency_id').values_list('agency_id', flat=True)
            if agency_ids:
                # Поиск смен
                shifts_list = OutsourcingShift.objects.filter(request__state='ready'). \
                    filter(Q(agency_id__in=agency_ids, request__organization=organization) |
                           Q(agency_id__in=agency_ids, request__organization__parent=organization)).filter(
                    state='accept')
                if month:
                    shifts_list = shifts_list.filter(Q(start__gte=month_start) & Q(start__lte=month_end))
                else:
                    shifts_list = shifts_list.filter(Q(start__gte=start) & Q(start__lte=end))

                shifts_list = shifts_list.select_related('request', 'job').values('start',
                                                                                  'agency_id',
                                                                                  'agency__name',
                                                                                  'request__organization_id',
                                                                                  'request__organization__name',
                                                                                  'job_id',
                                                                                  'job__name',
                                                                                  'job__color',
                                                                                  'job__icon'). \
                    annotate(dcount=Count('id'))

                # Получение максимального кол-ва смен из всех дней периода, т.к. в запросе выше нельзя сделать Max
                # от вычисляемого значения
                max_size = dict()
                for sh in shifts_list:
                    max_size[(sh['agency_id'], sh['job_id'])] = max(
                        max_size.get((sh['agency_id'], sh['job_id']), 0), sh['dcount'])

                # Создание блоков на основе данных того же запроса, чтобы не делать новый
                processed_list = []
                if shifts_list.exists():
                    # Добавляем собранную информацию об агентсве и его квотах
                    row_data = []
                    for row in shifts_list:
                        if (row['agency_id'], row['job_id']) in processed_list:
                            continue
                        store_data = {"id": row['agency_id'], "name": row['agency__name']}
                        area_data = {"id": f"{row['agency_id']}_{row['job_id']}",
                                     "name": row['job__name'],
                                     "icon": row['job__icon'], "color": row['job__color']}
                        row_data.append({"organization": store_data, "area": area_data,
                                         "size": max_size[(row['agency_id'], row['job_id'])]})
                        processed_list.append((row['agency_id'], row['job_id']))
                    blocks_data.append({"id": organization.id, "name": organization.name, "rows": row_data})
            # Поиск ранее спланированных смен
            shifts_list = OutsourcingShift.objects.filter(request__organization=organization). \
                filter(state='accept', request__state='ready')
            shifts_list = shifts_list.filter(start__gte=start, start__lte=end)

            if shifts_list.exists():
                current_row_index = dict()
                for shift in shifts_list:
                    urow_index = current_row_index.get(
                        (shift.request.organization_id, shift.job_id, shift.start), 0)
                    shift.urow_index = urow_index
                    current_row_index[
                        (shift.request.organization_id, shift.job_id, shift.start)] = urow_index + 1
                    if export:
                        shift_ids.append(shift.id)
                shifts_data.extend(OutsourcingShiftReadSerializer(shifts_list, many=True).data)

            # Выгрузка в Excel
            if export:
                return get_report_by_code(f'{party}shift', OutsourcingShift.objects.filter(id__in=shift_ids))

        elif mode in ['promo', 'broker']:
            # Поиск агентств, с которыми работает магазин
            promo_ids = OrgLink.objects.filter(Q(organization=organization) | Q(organization__parent=organization)). \
                order_by('aheadquarter_id').distinct('aheadquarter_id').values_list('aheadquarter_id', flat=True)
            if promo_ids:
                if mode == 'promo':
                    # Поиск квот на выбранного промоутера и ранее спланированных смен
                    quota_list = Quota.objects.filter(promo_id__in=promo_ids, store=organization)

                    if month:
                        quota_list = quota_list.filter(Q(start__lte=month_start, end__isnull=True) |
                                                       Q(start__lte=month_start, end__gte=month_end))
                    else:
                        quota_list = quota_list.filter(
                            Q(start__lte=start, end__isnull=True) | Q(start__lte=start, end__gte=end))

                    quota_list = quota_list.select_related('area', 'store', 'promo').order_by('store_id', '-start')
                    if quota_list.exists():
                        # Добавляем собранную информацию об агентсве и его квотах
                        # Ищем агентства, из компании промоутера, работающие в этом магазине
                        orglinks = OrgLink.objects.filter(
                            Q(organization=organization) | Q(organization__parent=organization)). \
                            order_by('agency_id').distinct('agency_id')
                        row_data = []
                        for quota in quota_list:
                            # Проверка, что квота является активной
                            if not quota.check_if_active(month):
                                continue
                            #
                            # TODO store_data -> agency_data
                            for orglink in orglinks:
                                store_data = {"id": orglink.agency.id, "name": orglink.agency.name}
                                area_data = {"id": quota.area.id, "name": quota.area.name, "color": quota.area.color,
                                             "icon": quota.area.icon}
                                # TODO organization -> agency
                                row_data.append({"organization": store_data, "area": area_data, "size": quota.value_total})
                        # Агентство + магазин
                        blocks_data.append({"id": organization.id, "name": organization.name, "rows": row_data})
                        has_quotas = True
                elif mode == 'broker':
                    # Поиск ранее спланированных смен
                    shifts_list = PromoShift.objects.filter(organization=organization).exclude(state='delete')

                    if month:
                        shifts_list = shifts_list.filter(Q(start__gte=month_start) & Q(start__lte=month_end))
                    else:
                        shifts_list = shifts_list.filter(Q(start__gte=start) & Q(start__lte=end))

                    shifts_list = shifts_list.select_related('organization', 'store_area').values('start',
                                                                                                  'agency_id',
                                                                                                  'agency__name',
                                                                                                  'organization_id',
                                                                                                  'organization__name',
                                                                                                  'store_area__id',
                                                                                                  'store_area__name',
                                                                                                  'store_area__color',
                                                                                                  'store_area__icon'
                                                                                                  ). \
                        annotate(dcount=Count('id'))

                    # Получение максимального кол-ва смен из всех дней периода, т.к. в запросе выше нельзя сделать Max
                    # от вычисляемого значения
                    max_size = dict()
                    for sh in shifts_list:
                        max_size[(sh['agency_id'], sh['organization_id'])] = max(
                            max_size.get((sh['agency_id'], sh['organization_id']), 0), sh['dcount'])

                    # Создание блоков на основе данных того же запроса, чтобы не делать новый
                    processed_list = []
                    if shifts_list.exists():
                        has_quotas = True
                        # Добавляем собранную информацию об агентсве и его сменах
                        row_data = []
                        for row in shifts_list:
                            if (row['agency_id'], row['organization_id']) in processed_list:
                                continue
                            store_data = {"id": row['agency_id'], "name": row['agency__name']}
                            area_data = {"id": row['store_area__id'],
                                         "name": row['store_area__name'],
                                         "icon": row['store_area__icon'], "color": row['store_area__color']}
                            row_data.append({"organization": store_data, "area": area_data,
                                             "size": max_size[(row['agency_id'], row['organization_id'])]})
                            processed_list.append((row['agency_id'], row['organization_id']))
                        blocks_data.append({"id": organization.id, "name": organization.name, "rows": row_data})

            # Поиск ранее спланированных смен
            shifts_list = PromoShift.objects.filter(organization=organization).exclude(state='delete')
            shifts_list = shifts_list.filter(start__gte=start, start__lte=end).select_related('organization__parent').\
                annotate(agency_city=F('agency_id'))

            # Поиск доступностей
            avails_list = Availability.objects.filter(organization=organization, start__gte=start,
                                                      start__lte=end).annotate(agency_city=F('agency_id'))

            if shifts_list.exists():
                if party == 'promo':
                    # Сотрудники с нарушениями по мед. книжке
                    violation_employee_ids = get_shift_violation_employee_ids(shifts_list)
                    violation_item = ViolationRuleItem.objects.filter(rule__code='medical', severity='high').order_by(
                        'value_from').first()
                for shift in shifts_list:
                    if party == 'promo':
                        days_value = violation_item.value_to if violation_item else 0
                        if shift.agency_employee_id and shift.start + timedelta(days=days_value) > \
                                violation_employee_ids[shift.agency_employee_id]:
                            shift.has_violations = True
                    if export:
                        shift_ids.append(shift.id)

                if has_quotas:
                    shifts_data.extend(PromoShiftReadSerializer(shifts_list, many=True).data)

                else:
                    diff_data.extend(PromoShiftReadSerializer(shifts_list, many=True).data)
            if avails_list:
                avails_data.extend(AvailabilityReadSerializer(avails_list, many=True).data)
        # Выгрузка в Excel
        if export:
            return get_report_by_code(f'{party}schedule', PromoShift.objects.filter(id__in=shift_ids))

    # Возвращем полученный результат
    return Response({"blocks": blocks_data, "shifts": shifts_data, "diff": diff_data, "avails": avails_data})


class ApiPromoShiftView(APIView, ):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    # parser_classes = (JSONParser,)
    page_codes = ['promo_schedule', 'broker_schedule']

    def _process_one_shift(self, request, shift_data, overwrite, silent):
        # Проверка корректности переданных данных
        if '_' in shift_data['agency_id']:
            shift_data = shift_data.copy()
            shift_data['agency_id'] = shift_data['agency_id'].split('_')[0]

        serializer = PromoShiftWriteSerializer(data=shift_data)
        serializer.is_valid(raise_exception=True)
        # ПРОВЕРКА ПРАВ ДОСТУПА (TODO - Кэшировать проверку)
        agency = serializer.validated_data['agency']
        if not check_struct_access_to_page(request.user, agency.headquater, agency, self.page_codes, "write"):
            raise ValidationError("AccessDenied")
        # ПРОВЕРКА ПОЛЕЙ
        promo_shift = serializer.find_instance(serializer.validated_data, overwrite)
        error = serializer.check_shift(promo_shift, serializer.validated_data)
        if error:
            if not silent:
                raise error
            return promo_shift
        # СОЗДАНИЕ \ РЕДАКТИРОВАНИЕ СМЕНЫ
        if promo_shift:
            previous_instance = open_promo_shift(promo_shift.id)
            new_instance = serializer.update(promo_shift, serializer.validated_data, request.user)
            promo_shift_new = open_promo_shift(new_instance.id)
            instance_diff = promo_shift_new.get_diff(previous_instance)
            log_handler = log_promo_shift_edit
            log_handler(user_id=request.user.id,
                        entity_id=promo_shift.id,
                        headquarter=promo_shift.headquarter_id,
                        promo=promo_shift.aheadquarter_id,
                        organization=promo_shift.organization_id,
                        agency=promo_shift.agency_id,
                        start=promo_shift.start,
                        end=promo_shift.end,
                        source_info=None,
                        diff=instance_diff,
                        store_area=promo_shift.store_area.name
                        )
        else:
            promo_shift = serializer.create(serializer.validated_data, request.user)
            # При создании новой смены

            instance_diff = {}
            log_handler = log_promo_shift_new
            log_handler(user_id=request.user.id,
                        entity_id=promo_shift.id,
                        headquarter=promo_shift.headquarter_id,
                        promo=promo_shift.aheadquarter_id,
                        organization=promo_shift.organization_id,
                        agency=promo_shift.agency_id,
                        start=promo_shift.start,
                        end=promo_shift.end,
                        source_info=None,
                        diff=instance_diff,
                        store_area=promo_shift.store_area.name
                        )
        promo_shift.agency_city = f"{promo_shift.agency_id}_{promo_shift.organization.parent_id}"
        return promo_shift

    def get(self, request):
        promo_shift = open_promo_shift(request.GET.get('shift_id', None))
        if not promo_shift:
            raise ValidationError("Undefined: shift_id")
        if not check_struct_access_to_page(request.user, promo_shift.aheadquarter, promo_shift.agency, self.page_codes,
                                           'read'):
            raise ValidationError("AccessDenied")
        if promo_shift.agency_employee:
            if check_violation_rules_exists_by_date(self.page_codes, promo_shift.agency_employee,
                                                    promo_shift.start_date):
                promo_shift.has_violations = True
        return Response(PromoShiftReturnSerializer({'shift': promo_shift}, many=False).data)

    def post(self, request):
        overwrite = strtobool(request.POST.get('overwrite', 'true'))
        shifts_list = []
        if 'shifts' in request.data:
            shifts_data = json.loads(request.data['shifts'])
            for shift_data in shifts_data:
                shift = self._process_one_shift(request, shift_data, overwrite, True)
                if shift:
                    shifts_list.append(shift)
        # Сохранение одного элемента
        else:
            shift = self._process_one_shift(request, request.data, overwrite, False)
            if shift:
                shifts_list.append(shift)
        # Возврат результата
        # Заполнение флага нарушений
        for shift in shifts_list:
            if shift.agency_employee:
                if check_violation_rules_exists_by_date(self.page_codes, shift.agency_employee, shift.start_date):
                    shift.has_violations = True
        return Response(PromoShiftReadSerializer(shifts_list, many=True).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        # @TODO в ресте DELETE не используется для группового удаления, для этого используется команда POST
        shifts_list = json.loads(request.data.get('shift_ids', '[]'))
        for shift_id in shifts_list:
            shift = open_promo_shift(shift_id)
            # Удаляем, если объект существует и у пользователя есть необходимые права доступа
            if shift:
                if check_struct_access_to_page(request.user, shift.aheadquarter, shift.agency, self.page_codes,
                                               "write"):
                    instance_diff = {}
                    log_handler = log_promo_shift_del
                    log_handler(user_id=request.user.id,
                                entity_id=shift.id,
                                headquarter=shift.headquarter_id,
                                promo=shift.aheadquarter_id,
                                organization=shift.organization_id,
                                agency=shift.agency_id,
                                start=shift.start,
                                end=shift.end,
                                source_info=None,
                                diff=instance_diff,
                                store_area=shift.store_area.name
                                )
                    shift.remove()
                else:
                    raise ValidationError('AccessDenied')
        return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)


@login_required
@api_view(['GET', 'POST', 'DELETE'])
def api_promo_shift(request):
    """
    API endpoint, работает в следующих двух режимах:
    - GET - вывод информации о смене промоутера/кредитного брокера
    - POST - создание / редактирование одной или нескольких смеен
    - DELETE - удаление смены
    """
    current_user = request.user
    page_codes = ['promo_schedule', 'broker_schedule']

    # GET - Получение данных по выбранной смене
    if request.method == 'GET':
        # Поиск объекта смены 
        promo_shift = open_promo_shift(request.GET.get('shift_id', None))
        if not promo_shift:
            return make_error_response("Undefined: shift_id")
        # ПРОВЕРКА ПРАВ ДОСТУПА
        if not check_struct_access_to_page(current_user, promo_shift.aheadquarter, promo_shift.agency, page_codes,
                                           'read'):
            return make_error_response("AccessDenied")
        # Формируем ответное сообщение
        # Заполнение флага нарушений
        if promo_shift.agency_employee:
            if check_violation_rules_exists_by_date(page_codes, promo_shift.agency_employee, promo_shift.start_date):
                promo_shift.has_violations = True
        return Response({"shift": PromoShiftReadSerializer(promo_shift, many=False).data})

    # POST - Создание, редактирование
    elif request.method == 'POST':
        # Обработка одного элемента
        def process_one_shift(shift_data, overwrite, silent):
            # Проверка корректности переданных данных
            if '_' in shift_data['agency_id']:
                shift_data = shift_data.copy()
                shift_data['agency_id'] = shift_data['agency_id'].split('_')[0]
            serializer = PromoShiftWriteSerializer(data=shift_data)
            if not serializer.is_valid():
                return serializer.errors, None
            # ПРОВЕРКА ПРАВ ДОСТУПА (TODO - Кэшировать проверку)
            agency = serializer.validated_data['agency']
            if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, "write"):
                return "AccessDenied", None
            # ПРОВЕРКА ПОЛЕЙ
            promo_shift = serializer.find_instance(serializer.validated_data, overwrite)
            error = serializer.check_shift(promo_shift, serializer.validated_data)
            if error:
                error = error if not silent else None
                return error, promo_shift
            # СОЗДАНИЕ \ РЕДАКТИРОВАНИЕ СМЕНЫ
            if promo_shift:
                previous_instance = open_promo_shift(promo_shift.id)
                new_instance = serializer.update(promo_shift, serializer.validated_data, current_user)
                promo_shift_new = open_promo_shift(new_instance.id)
                instance_diff = promo_shift_new.get_diff(previous_instance)
                log_handler = log_promo_shift_edit
                log_handler(user_id=request.user.id,
                            entity_id=promo_shift.id,
                            headquarter=promo_shift.headquarter_id,
                            promo=promo_shift.aheadquarter_id,
                            organization=promo_shift.organization_id,
                            agency=promo_shift.agency_id,
                            start=promo_shift.start,
                            end=promo_shift.end,
                            source_info=None,
                            diff=instance_diff,
                            store_area=promo_shift.store_area.name
                            )
            else:
                promo_shift = serializer.create(serializer.validated_data, current_user)
                # При создании новой смены
                from apps.shifts.methods import get_or_create_quota_info
                promo_shift.quota_info = get_or_create_quota_info(promo_shift)
                promo_shift.quota_info.shifts_count += 1
                if not promo_shift.agency_employee:
                    promo_shift.quota_info.open_shifts_count += 1
                promo_shift.quota_info.save()
                promo_shift.save()
                instance_diff = {}
                log_handler = log_promo_shift_new
                log_handler(user_id=request.user.id,
                            entity_id=promo_shift.id,
                            headquarter=promo_shift.headquarter_id,
                            promo=promo_shift.aheadquarter_id,
                            organization=promo_shift.organization_id,
                            agency=promo_shift.agency_id,
                            start=promo_shift.start,
                            end=promo_shift.end,
                            source_info=None,
                            diff=instance_diff,
                            store_area=promo_shift.store_area.name
                            )
            return None, promo_shift

        # Признак перезаписи поверх существующих смен
        overwrite = request.POST.get('overwrite', 'false').capitalize()

        # Сохранение массива данных
        shifts_list = []
        if 'shifts' in request.data:
            shifts_data = json.loads(request.data['shifts'])
            for shift_data in shifts_data:
                error, shift = process_one_shift(shift_data, overwrite, True)
                if error:
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)
                if shift:
                    shifts_list.append(shift)
        # Сохранение одного элемента
        else:
            error, shift = process_one_shift(request.data, overwrite, False)
            if error:
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            if shift:
                shifts_list.append(shift)
        # Возврат результата
        # Заполнение флага нарушений
        for shift in shifts_list:
            if shift.agency_employee:
                if check_violation_rules_exists_by_date(page_codes, shift.agency_employee, shift.start_date):
                    shift.has_violations = True
        return Response(PromoShiftReadSerializer(shifts_list, many=True).data, status=status.HTTP_201_CREATED)

    # DELETE - Удаление смены
    elif request.method == 'DELETE':
        shifts_list = json.loads(request.data['shift_ids']) if 'shift_ids' in request.data else []
        # Удаление объектов смен
        for shift_id in shifts_list:
            shift = open_promo_shift(shift_id)
            # Удаляем, если объект существует и у пользователя есть необходимые права доступа
            if shift:
                if check_struct_access_to_page(current_user, shift.aheadquarter, shift.agency, page_codes, "write"):
                    instance_diff = {}
                    log_handler = log_promo_shift_del
                    log_handler(user_id=request.user.id,
                                entity_id=shift.id,
                                headquarter=shift.headquarter_id,
                                promo=shift.aheadquarter_id,
                                organization=shift.organization_id,
                                agency=shift.agency_id,
                                start=shift.start,
                                end=shift.end,
                                source_info=None,
                                diff=instance_diff,
                                store_area=shift.store_area.name
                                )
                    # TODO убрать в метод объекта
                    if shift.quota_info:
                        shift.quota_info.shifts_count -= 1
                        if not shift.agency_employee:
                            shift.quota_info.open_shifts_count -= 1
                        shift.quota_info.save()
                    shift.remove()
                else:
                    return make_error_response('AccessDenied')
        return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)

    # Неизвестный метод    
    return make_error_response('UnknownError')


@login_required
@api_view(['GET'])
def api_free_employees(request):
    """
    API endpoint, работает в двух режимах в зависимости от значения параметра employee_id,
    - если параметр задан, то проверка выполняется только для заданного сотрудника
    - в противном случае - выполняется поиск всех подходящих клиентов
    """
    current_user = request.user
    page_codes = ['promo_schedule', 'broker_schedule', 'outsource_schedule']

    # Считываем данные из запроса
    # - время начала и окончания смены
    if not 'start' in request.GET:
        return make_error_response('Undefined: start')
    start = dateparse.parse_datetime(request.GET['start'])
    if not 'end' in request.GET:
        return make_error_response('Undefined: end')
    end = dateparse.parse_datetime(request.GET['end'])
    # - тип
    party = request.GET.get('party', 'promo')
    # - агентство
    agency = request.GET.get('agency_id', None)
    if '_' in agency:
        agency = agency.split('_')[0]
    agency = open_agency(agency)

    if not agency:
        return make_error_response("Undefined: agency_id")
    # - магазин
    organization = open_organization(request.GET.get('organization_id', None))
    if not organization:
        return make_error_response("Undefined: organization_id")
    # - смена (поле задается, если проверка требуется для существующей смены)
    shift_ids = [request.GET['shift_id']] if 'shift_id' in request.GET else []
    # - должность (используется только для смен аутсорсинга)
    job = open_job(request.GET.get('job_id', None))
    # - вкладка (основная или остальные сотрудники)
    tab = request.GET.get('tab', 'main')
    # - строка поиска
    search = request.GET.get('search')

    # ПРОВЕРКА ПРАВ ДОСТУПА
    if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, 'read'):
        return make_error_response("AccessDenied")

    # TODO
    # Если передан конкретный сотрудник, то проверяем, может ли он быть назначен на смену
    employee = open_employee(request.GET.get('agency_employee_id', None))
    if employee:
        employee.selectable = can_set_employee_to_shft_ext(employee, start, end, agency, organization.headquater, job,
                                                           shift_ids)
        return Response({"employees": [{'id': employee.id,
                                        'text': employee.name,
                                        'selectable': employee.selectable,
                                        'violation_text':
                                            check_violation_rules_by_date(page_codes, agency.headquater, employee)[
                                                0] if party != 'agency' and check_violation_rules_by_date(page_codes,
                                                                                                          agency.headquater,
                                                                                                          employee) else None
                                        }]})
    # Иначе - формируем список сотрудников
    else:
        # TODO
        if tab == 'all':
            employees = query_free_employees_for_shift_ext(agency, organization.headquater, start, end, job, shift_ids)
        else:
            employees = query_free_employees_for_shift_ext(agency, organization, start, end, job, shift_ids)
        if search:
            # Поиск сотрудников
            employees = make_search(
                query_free_employees_for_shift_ext(agency, organization.headquater, start, end, job, shift_ids, True),
                search)[:10]

        employees_list = list()
        # TODO ПЕРЕДЕЛАТЬ
        if party == 'promo':
            medical_violation_employees = get_period_violation_employee_ids(employees, start, end)
            files_violation_employees = get_period_violation_employee_ids(employees, start, end, True)
            for employee in employees:
                selectable = True
                violation_text = ''
                if employee.id not in medical_violation_employees:
                    selectable = False
                    violation_text = 'Мед. книжка отсутствует'
                elif employee.id not in files_violation_employees:
                    # @TODO Есть ощущение, что этот кусок кода сделан неправильно, начиная с ПЕРЕДЕЛАТЬ
                    vri = ViolationRuleItem.objects.filter(value_from=0, rule__code='medical_no_files', ).first()
                    if vri and vri.severity == 'high':
                        selectable = False
                    else:
                        selectable = True
                    violation_text = 'Файл мед. книжки отсутствует'

                if search:
                    # Получаем смены сотрудника на эту дату
                    employee_shifts = PromoShift.objects.filter(agency_employee=employee,
                                                                start__lte=end,
                                                                end__gte=start). \
                        exclude(state='delete'). \
                        exclude(id__in=shift_ids). \
                        values_list('organization__name', flat=True)
                    if employee_shifts:
                        selectable = False
                        violation_text = f'Cотрудник занят в магазине {employee_shifts[0]}'

                employees_list.append({'id': employee.id,
                                       'text': employee.name,
                                       'selectable': selectable,
                                       'city': employee.cities_export,
                                       'violation_text': violation_text
                                       })
        else:
            for employee in employees:
                selectable = True
                violation_text = ''
                if search:
                    # Получаем смены сотрудника на эту дату
                    employee_shifts = OutsourcingShift.objects.filter(agency_employee=employee,
                                                                      start__lte=end,
                                                                      end__gte=start). \
                        exclude(id__in=shift_ids). \
                        values_list('request__organization__name', flat=True)
                    if employee_shifts:
                        selectable = False
                        violation_text = f'Cотрудник занят в магазине {employee_shifts[0]}'
                employees_list.append({'id': employee.id,
                                       'text': employee.name,
                                       'selectable': selectable,
                                       'city': employee.cities_export,
                                       'violation_text': violation_text
                                       })
        employees_list.sort(key=itemgetter('selectable'), reverse=True)
        return Response({"employees": employees_list})


class ApiAvailabilityView(APIView, ):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    page_codes = ['client_schedule']

    def _process_one_avail(self, request, avail_data, overwrite, silent):
        # Проверка корректности переданных данных
        serializer = AvailabilityWriteSerializer(data=avail_data)
        serializer.is_valid(raise_exception=True)


        # ПРОВЕРКА ПРАВ ДОСТУПА (TODO - Кэшировать проверку)
        organization = serializer.validated_data['organization']
        if not check_struct_access_to_page(request.user, organization.headquater, organization, self.page_codes,
                                           "write"):
            raise ValidationError({'non_field_errors': ["AccessDenied"]})
        # ПРОВЕРКА ПОЛЕЙ
        availability = serializer.find_instance(serializer.validated_data, overwrite)
        error = serializer.check_availability(availability, serializer.validated_data)
        if error:
            if not silent:
                raise ValidationError({'non_field_errors': [error]})
            return availability
        # СОЗДАНИЕ \ РЕДАКТИРОВАНИЕ СМЕНЫ
        if availability:
            previous_instance = open_availability(availability.id)
            new_instance = serializer.update(availability, serializer.validated_data, request.user)
            availability_new = open_availability(new_instance.id)
            instance_diff = availability_new.get_diff(previous_instance)
            log_handler = log_avail_edit
            log_handler(user_id=request.user.id,
                        entity_id=availability.id,
                        headquarter=availability.headquarter_id,
                        promo=availability.aheadquarter_id,
                        organization=availability.organization_id,
                        agency=availability.agency_id,
                        start=availability.start,
                        end=availability.end,
                        source_info=None,
                        diff=instance_diff,
                        store_area=availability.store_area.name
                        )
        else:
            availability = serializer.save()
            instance_diff = {}
            log_handler = log_avail_new
            log_handler(user_id=request.user.id,
                        entity_id=availability.id,
                        headquarter=availability.headquarter_id,
                        promo=availability.aheadquarter_id,
                        organization=availability.organization_id,
                        agency=availability.agency_id,
                        start=availability.start,
                        end=availability.end,
                        source_info=None,
                        diff=instance_diff,
                        store_area=availability.store_area.name
                        )
        return availability

    def get(self, request):
        availability = open_availability(request.GET.get('avail_id', None))
        if not availability:
            raise ValidationError({'non_field_errors': ["Undefined: avail_id"]})
        # ПРОВЕРКА ПРАВ ДОСТУПА
        if not check_struct_access_to_page(request.user, availability.headquarter, availability.organization,
                                           self.page_codes, 'read'):
            raise ValidationError({'non_field_errors': ["AccessDenied"]})
        # Формируем ответное сообщение
        return Response(AvailabilityReturnSerializer({'avail': availability}, many=False).data)

    def post(self, request):
        overwrite = strtobool(request.POST.get('overwrite', 'false'))

        # Сохранение массива данных
        avails_list = []
        if 'avails' in request.data:
            avails_data = json.loads(request.data['avails'])
            for avail_data in avails_data:
                avail = self._process_one_avail(request, avail_data, overwrite, True)
                avail.agency_city = f"{avail.agency_id}_{avail.organization.parent_id}"
                if avail:
                    avails_list.append(avail)
        # Сохранение одного элемента
        else:
            avail = self._process_one_avail(request, request.data, overwrite, False)
            if avail:
                avail.agency_city = f"{avail.agency_id}_{avail.organization.parent_id}"
                avails_list.append(avail)
        # Возврат результата

        return Response(AvailabilityReadSerializer(avails_list, many=True).data, status=status.HTTP_201_CREATED)

    def delete(self, request):
        # @TODO в ресте DELETE не используется для группового удаления, для этого используется команда POST
        avails_list = json.loads(request.data['avail_ids']) if 'avail_ids' in request.data else []
        # Удаление объектов доступностей
        for avail_id in avails_list:
            availability = open_availability(avail_id)
            # Удаляем, если объект существует и у пользователя есть необходимые права доступа
            if availability:
                if check_struct_access_to_page(request.user, availability.headquarter, availability.organization,
                                               self.page_codes, "write"):
                    instance_diff = {}
                    log_handler = log_avail_del
                    log_handler(user_id=request.user.id,
                                entity_id=availability.id,
                                headquarter=availability.headquarter_id,
                                promo=availability.aheadquarter_id,
                                organization=availability.organization_id,
                                agency=availability.agency_id,
                                start=availability.start,
                                end=availability.end,
                                source_info=None,
                                diff=instance_diff,
                                store_area=availability.store_area.name
                                )
                    availability.delete()
                else:
                    raise ValidationError({'non_field_errors': ["AccessDenied"]})
        return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)


@login_required
@api_view(['GET', 'POST', 'DELETE'])
def api_availability(request):
    """
    API endpoint, работает в следующих двух режимах:
    - GET - вывод информации о доступности
    - POST - создание / редактирование одной или доступностей
    - DELETE - удаление доступности
    """
    current_user = request.user
    page_codes = ['client_schedule']

    # GET - Получение данных по выбранной смене
    if request.method == 'GET':
        # Поиск объекта смены
        availability = open_availability(request.GET.get('avail_id', None))
        if not availability:
            return make_error_response("Undefined: avail_id")
        # ПРОВЕРКА ПРАВ ДОСТУПА
        if not check_struct_access_to_page(current_user, availability.headquarter, availability.organization,
                                           page_codes, 'read'):
            return make_error_response("AccessDenied")
        # Формируем ответное сообщение
        return Response({"avail": AvailabilityReadSerializer(availability, many=False).data})

    # POST - Создание, редактирование
    elif request.method == 'POST':

        # Обработка одного элемента
        def process_one_avail(avail_data, overwrite, silent):
            # Проверка корректности переданных данных
            serializer = AvailabilityWriteSerializer(data=avail_data)
            if not serializer.is_valid():
                return serializer.errors, None
            # ПРОВЕРКА ПРАВ ДОСТУПА (TODO - Кэшировать проверку)
            organization = serializer.validated_data['organization']
            if not check_struct_access_to_page(current_user, organization.headquater, organization, page_codes,
                                               "write"):
                return "AccessDenied", None
            # ПРОВЕРКА ПОЛЕЙ
            availability = serializer.find_instance(serializer.validated_data, overwrite)
            error = serializer.check_availability(availability, serializer.validated_data)
            if error:
                error = error if not silent else None
                return error, availability
            # СОЗДАНИЕ \ РЕДАКТИРОВАНИЕ СМЕНЫ
            if availability:
                previous_instance = open_availability(availability.id)
                new_instance = serializer.update(availability, serializer.validated_data, current_user)
                availability_new = open_availability(new_instance.id)
                instance_diff = availability_new.get_diff(previous_instance)
                log_handler = log_avail_edit
                log_handler(user_id=request.user.id,
                            entity_id=availability.id,
                            headquarter=availability.headquarter_id,
                            promo=availability.aheadquarter_id,
                            organization=availability.organization_id,
                            agency=availability.agency_id,
                            start=availability.start,
                            end=availability.end,
                            source_info=None,
                            diff=instance_diff,
                            store_area=availability.store_area.name
                            )
            else:
                availability = serializer.save()
                instance_diff = {}
                log_handler = log_avail_new
                log_handler(user_id=request.user.id,
                            entity_id=availability.id,
                            headquarter=availability.headquarter_id,
                            promo=availability.aheadquarter_id,
                            organization=availability.organization_id,
                            agency=availability.agency_id,
                            start=availability.start,
                            end=availability.end,
                            source_info=None,
                            diff=instance_diff,
                            store_area=availability.store_area.name
                            )
            return None, availability

        # Признак перезаписи поверх существующих доступностей
        overwrite = strtobool(request.POST.get('overwrite', 'false'))

        # Сохранение массива данных
        avails_list = []
        if 'avails' in request.data:
            avails_data = json.loads(request.data['avails'])
            for avail_data in avails_data:
                error, avail = process_one_avail(avail_data, overwrite, True)
                if error:
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)
                if avail:
                    avails_list.append(avail)
        # Сохранение одного элемента
        else:
            error, avail = process_one_avail(request.data, overwrite, False)
            if error:
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
            if avail:
                avails_list.append(avail)
        # Возврат результата
        return Response(AvailabilityReadSerializer(avails_list, many=True).data, status=status.HTTP_201_CREATED)

    # DELETE - Удаление доступности
    elif request.method == 'DELETE':
        avails_list = json.loads(request.data['avail_ids']) if 'avail_ids' in request.data else []
        # Удаление объектов доступностей
        for avail_id in avails_list:
            availability = open_availability(avail_id)
            # Удаляем, если объект существует и у пользователя есть необходимые права доступа
            if availability:
                if check_struct_access_to_page(current_user, availability.headquarter, availability.organization,
                                               page_codes, "write"):
                    instance_diff = {}
                    log_handler = log_avail_del
                    log_handler(user_id=request.user.id,
                                entity_id=availability.id,
                                headquarter=availability.headquarter_id,
                                promo=availability.aheadquarter_id,
                                organization=availability.organization_id,
                                agency=availability.agency_id,
                                start=availability.start,
                                end=availability.end,
                                source_info=None,
                                diff=instance_diff,
                                store_area=availability.store_area.name
                                )
                    availability.delete()
                else:
                    return make_error_response('AccessDenied')
        return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)

    # Неизвестный метод
    return make_error_response('UnknownError')


class ApiExportEmployeeShiftsView(APIView, ):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    # parser_classes = (JSONParser,)
    page_codes = ['employees_list', 'hq_employees_list', 'promo_employees_list', 'broker_employees_list']

    def get(self, request):
        serializer = ApiExportEmployeeShiftsRequestSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        start = serializer.validated_data['start']
        end = serializer.validated_data['end']
        employee_list = serializer.validated_data['employee_list']

        # Определение типа смен для поиска
        shifts_type = None
        for employee_id in employee_list:
            if shifts_type:
                break
            employee = open_employee(employee_id)
            if not employee:
                continue
            # Определение типа смен
            if not shifts_type:
                shifts_type = employee.agency.headquater.party

        if shifts_type == 'agency':
            shifts = OutsourcingShift
        else:
            shifts = PromoShift

        # Поиск всех смен
        shifts = shifts.objects.all()
        # Фильтрация по идентификатору сотрудника
        shifts = shifts.filter(agency_employee__in=employee_list)
        # Фильтрация смен по периоду
        shifts = shifts.filter(start_date__lte=end, start_date__gte=start).order_by('agency_employee__surname',
                                                                                    'agency_employee__firstname',
                                                                                    'agency_employee__patronymic')

        # Передача queryset смен на формирование отчета
        return get_report_by_code(f"{shifts_type}_export_employee_shifts", shifts)


class RedirectPromoShiftGuid(APIView):
    def get(self, request):
        if request.GET.get('guid'):

            try:
                ps = PromoShift.objects.get(guid=request.GET.get('guid'))
                return redirect(f"https://outsourcing.verme.ru/admin/shifts/promoshift/{ps.id}/change/")
            except PromoShift.DoesNotExist:
                pass
        return Response({'error':'нет такой смены'})

