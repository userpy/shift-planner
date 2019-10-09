#
# Copyright 2018 ООО «Верме»
#
# Файл представлений претензий
#
# Для работы нужен permission/methods.py, который содержит проверку прав доступа;
# rest_framework, outsource/serializers.py, который содержит serializers для методов api
#

import calendar
import datetime
import uuid

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.http import HttpResponseBadRequest, HttpResponse
from django.db import IntegrityError
from django.db.models import F, Max
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.claims.models import ClaimRequest, ClaimAttach, ClaimMessage, ClaimHistory, ClaimStatus, ClaimType, ClaimAction, Document
from apps.claims.serializers import ClaimSerializer, ClaimMessageSerializer, ClaimTypeSerializer2, \
    ClaimAttachSerializer2, DocumentSerializer, AttachmentUploadSerializer

from apps.notifications.methods import make_notify_data

from apps.outsource.serializers import OrganizationSerializer4, AgencySerializer2
from apps.outsource.models import Headquater, Organization, Agency, Job, OrgLink, Config, PARTY_CHOICES

from apps.permission.decorators import check_page_permission_by_user
from apps.permission.methods import get_available_clients_by_user, check_struct_access_to_page, get_client_base_org, check_unit_permission_by_user
from apps.lib.methods import make_pagination, make_sort, make_error_response
from wfm import settings
from xlsexport.methods import get_report_by_code

from .methods import make_claims_queryset
from apps.outsource.methods import get_unit_list_downwards, open_orgunit, open_headquarter, open_agency, \
    open_organization, open_storearea, open_quota, open_job, open_headquarter_by_code, open_organization_by_code

# Претензии

@login_required
@check_page_permission_by_user
def claims_list(request, **context):
    # TODO счетчики
    context.update({"claim_count": 0, "request_count": 0})
    return render(request, "claims/claims_list.html", context)


@login_required
@check_page_permission_by_user
def promo_claims_list(request, **context):
    return render(request, "claims/claims_list.html", context)

@login_required
@check_page_permission_by_user
def broker_claims_list(request, **context):
    return render(request, "claims/claims_list.html", context)


@login_required
@check_page_permission_by_user
def hq_claims_list(request, **context):
    return render(request, "claims/hq_claims_list.html", context)


@login_required
@check_page_permission_by_user
def claim(request, **context):
    headquater_list = get_available_clients_by_user(request.user)
    claim_id = request.GET.get('id', None)
    max_filesize_config = None

    if claim_id:
        claim = ClaimRequest.objects.filter(id=claim_id).first()
        context['disabled'] = "disabled"
        context['claim_id'] = claim.id
        context['claim_status'] = claim.status
        # Если претензия уже существует - проверка размера будет для сообщения
        if claim:
            max_filesize_config = Config.objects.filter(headquater_id=claim.headquater_id, key='max_file_size').first()
        # TODO счетчики
        context.update({"claim_count": 0, "request_count": 0})

    if len(headquater_list) != 0:
        # Если претензия существует, или создается
        # TODO убрать list
        max_filesize_config = Config.objects.filter(headquater_id=headquater_list[0]['id'], key='max_file_size').first()

    if not max_filesize_config:
        max_filesize = '1'
    else:
        max_filesize = max_filesize_config.value
    context.update({"max_filesize": max_filesize})
    context.update({"is_org_select_disabled": True})

    if not claim_id:
        context.update({"guid": str(uuid.uuid4())})

    return render(request, "claims/claim.html", context)


@xframe_options_exempt
def claim_frame(request):
    # Если вместе с запросом передали авторизационный токен
    key = request.GET.get('authorize_key', None)
    # Если вместе с запросом передали код организации
    organization = request.GET.get('organization', None)
    # Если вместе с запросом передали код клиента
    headquater = request.GET.get('headquater', None)
    # Если вместе с запросом передали ФИО пользователя
    user_name = request.GET.get('user_name', None)
    # Если передан user_name его нужно
    if user_name:
        from requests.utils import unquote
        user_name = unquote(user_name)
    # Если вместе с запросом передали email пользователя
    email = request.GET.get('email', None)
    # Если передано начало и конец периода
    period_start = request.GET.get('period_start', None)
    period_end = request.GET.get('period_end', None)

    # По умолчанию не определено
    # (если вдруг не переданы organization и headquater)
    max_filesize_config = None
    org_found = None

    # Проверка сущестования организационной единицы
    if organization and headquater:
        org_found = Organization.objects.filter(code=organization, headquater__code=headquater).first()
        # Передача ограничений на размер файлов
        max_filesize_config = Config.objects.filter(headquater__code=headquater, key='max_file_size').first()

    if not max_filesize_config:
        max_filesize = '1'
    else:
        max_filesize = max_filesize_config.value

    return render(request, "claims/claim_frame.html", {"key": key,
                                                       "organization": organization,
                                                       "headquater": headquater,
                                                       "period_start": period_start,
                                                       "period_end": period_end,
                                                       "user_name": user_name,
                                                       "email": email,
                                                       "max_filesize": max_filesize,
                                                       "org_found": org_found,
                                                       "DEBUG": settings.DEBUG
                                                       })


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def api_get_claims(request):
    """API endpoint для получения списка претензий
    принимает параметры:
    agency_id или headquater_id типа int (1)
    возвращает список job_history [{'id':, 'job':, 'start':, 'end':}]
    """
    # Доступные страницы
    page_codes = ['claims_list', 'hq_claims_list', 'promo_claims_list', 'broker_claims_list']
    current_user = request.user

    """Определяем орг. единицу"""
    unit_headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    if not unit_headquarter:
        unit_headquarter = open_headquarter_by_code(request.GET.get('headquater_code', None))
        unit = open_organization_by_code(request.GET.get('orgunit_code', None), unit_headquarter)

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

    """Получаем period_start из запроса"""
    period_start = request.GET.get('period_start', None)

    """Получаем period_end из запроса"""
    period_end = request.GET.get('period_end', None)

    """Формирование queryset для запроса"""
    query_set = make_claims_queryset(unit_headquarter, unit, date, period_start, period_end)

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
    status = request.GET.get('status_code', 'all')
    if status != 'all':
        query_set = query_set.filter(status__code=status)

    """Фильтры"""
    agency_list = filter_query_set.order_by('agency_id').\
        distinct('agency_id').select_related('agency').values('agency_id', 'agency__name').\
        annotate(id=F('agency_id'), text=F('agency__name')).values('id', 'text')
    organization_list = filter_query_set.select_related('organization').order_by('organization_id').\
        distinct('organization_id').values('organization_id', 'organization__name').\
        annotate(id=F('organization_id'), text=F('organization__name')).values('id', 'text')

    """Сортировка"""
    sort_fields = [
        'number',
        'organization__name',
        'organization__parent__name',
        'agency__name',
        'claim_type',
        'status__name',
        'dt_created',
        'dt_updated',
        'dt_status_changed'
    ]
    query_set = make_sort(query_set, sort_fields, request.GET.get(u'sort[field]', None),
                          request.GET.get(u'sort[sort]', 'desc'))

    """Файлы и последнее сообщение по претензиям"""
    for claim in query_set:
        attachments = ClaimAttach.objects.filter(claim=claim, message__isnull=True)
        if attachments:
            attachments_list = []
            for attachment in attachments:
                attachments_list.append(attachment)
            claim.attachments = attachments_list
        last_message = ClaimMessage.objects.filter(claim=claim).order_by('dt_created').first()
        if last_message:
            claim.dt_last_message = last_message.dt_created

    # Выгрузка в Excel
    export = request.GET.get('xlsexport', None)
    if export:
        return get_report_by_code('claim', query_set)

    """Пагинация"""
    query_set, meta = make_pagination(
        query_set,
        request.GET.get('pagination[page]', 1),
        request.GET.get('pagination[perpage]', 10)
    )

    # Формируем ответное сообщение
    ref_data = dict()
    ref_data['meta'] = meta
    ref_data['data'] = ClaimSerializer(query_set, many=True).data
    ref_data['agency_list'] = list(agency_list)
    ref_data['org_list'] = list(organization_list)

    return Response(ref_data)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def api_get_claim_messages(request):
    """API endpoint для получения списка сообщений по претензии
    принимает параметры:
    claim_id типа int (1)
    возвращает список job_history [{'id':, 'job':, 'start':, 'end':}]
    """
    # Доступные страницы
    page_codes = ['claim', 'hq_claim', 'promo_claim', 'broker_claim']

    if request.method == 'GET':
        """Получаем claim_id из запроса и фильтруем queryset на основе claim"""
        claim_id = request.GET.get('claim_id', None)

        # Если не передали claim_id
        if not claim_id:
            return HttpResponseBadRequest("No parameters")

        # Если передали claim_id
        try:
            claim_id = int(claim_id)
            claim = ClaimRequest.objects.filter(id=claim_id).first()
        except:
            return HttpResponseBadRequest("Bad parameters")

        if not claim:
            return HttpResponseBadRequest("No claim")

        """Проверка прав доступа"""
        if not check_unit_permission_by_user(request.user, [claim.agency, claim.organization], page_codes, 'read'):
            return HttpResponseBadRequest("No permission")

        # Запрос на список сообщений по претензии
        query_set = ClaimMessage.objects.filter(claim=claim).order_by('-dt_created')

        # Файлы по сообщениям
        for message in query_set:
            if message.party == 'agency':
                message.party_detail = message.claim.agency.name
            else:
                message.party_detail = message.claim.organization.name
            attachments = ClaimAttach.objects.filter(message=message)
            if attachments:
                attachments_list = []
                for attachment in attachments:
                    attachments_list.append(attachment)
                message.attachments = attachments_list

        # История согласований
        from django.db.models import CharField, Value as V
        from django.db.models.functions import Concat
        # Запрос историю согласований по претензии
        query_set2 = ClaimHistory.objects.filter(claim=claim).order_by('-dt_created'). \
            annotate(text=Concat(F('state_from__name'), V(' -> '), F('state_to__name'), V('. '), F('comment'),
                                 output_field=CharField()))

        """Пагинация"""
        total = query_set.count() + query_set2.count()
        """Определяем отображаемую страницу и заявки на ней"""
        perpage = int(request.GET.get('pagination[perpage]', 10))  # количество на странице
        pages = int(total / perpage) + 1  # всего страниц
        page = int(request.GET.get('pagination[page]', 1))  # текущая страница
        if page > pages:
            page = 1
        first_record = (page - 1) * perpage  # с какой записи брать
        last_record = first_record + perpage  # и по какую

        ref_data = dict()
        ref_data['meta'] = {
            'page': page,
            'pages': pages,
            'perpage': perpage,
            'total': total
        }

        # Объединение списков и выбор диапазона
        full_list = merge_sorted_lists(list(query_set), list(query_set2))[first_record:last_record]

        """Сортировка"""
        sort_field = request.GET.get(u'sort[field]', None)
        allowed_sort_fields = [
            'id',
            'party',
            'user_name',
            'dt_created'
        ]
        if sort_field and sort_field in allowed_sort_fields:
            sort_order = request.GET.get(u'sort[sort]', 'desc')
            if sort_order == 'asc':
                reverse = False
            else:
                reverse = True
            if sort_field == 'id':
                full_list.sort(key=lambda d: d.id, reverse=reverse)
            if sort_field == 'party':
                full_list.sort(key=lambda d: d.party, reverse=reverse)
            if sort_field == 'user_name':
                full_list.sort(key=lambda d: d.user_name, reverse=reverse)
            if sort_field == 'dt_created':
                full_list.sort(key=lambda d: d.dt_created, reverse=reverse)
        ref_data['data'] = ClaimMessageSerializer(full_list, many=True).data
        return Response(ref_data)


def merge_sorted_lists(l1, l2):
    """
    Объединение сообщений и истории претензии

    Аргументы:
    - `l1`: Отсортированный список сообщений
    - `l2`: Отсортированный список претензий
    """
    sorted_list = []

    # Copy both the args to make sure the original lists are not
    # modified
    l1 = l1[:]
    l2 = l2[:]

    while l1 and l2:
        if l1[0].dt_created <= l2[0].dt_created:  # Сравниваем даты создания
            item = l2.pop(0)  # Убираем из списка
            sorted_list.append(item)
        else:
            item = l1.pop(0)
            sorted_list.append(item)

    # Добавляем оставшиеся элементы
    sorted_list.extend(l1 if l1 else l2)

    return sorted_list


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def api_get_claim_files(request):
    """API endpoint для получения списка файлов по претензии
    принимает параметры:
    claim_id типа int (1)
    возвращает список job_history [{'id':, 'job':, 'start':, 'end':}]
    """
    # Доступные страницы
    page_codes = ['claim', 'hq_claim', 'promo_claim', 'broker_claim']

    if request.method == 'GET':
        """Получаем claim_id из запроса и фильтруем queryset на основе claim"""
        claim_id = request.GET.get('claim_id', None)

        # Если не передали claim_id
        if not claim_id:
            return HttpResponseBadRequest("No parameters")

        # Если передали claim_id
        try:
            claim_id = int(claim_id)
            claim = ClaimRequest.objects.filter(id=claim_id).first()
        except:
            return HttpResponseBadRequest("Bad parameters")

        if not claim:
            return HttpResponseBadRequest("No claim")

        """Проверка прав доступа"""
        if not check_unit_permission_by_user(request.user, [claim.agency, claim.organization], page_codes, 'read'):
            return HttpResponseBadRequest("No permission")

        # Запрос на список файлов по претензии
        query_set = ClaimAttach.objects.filter(claim=claim).order_by('-dt_created')

        """Сортировка"""
        sort_field = request.GET.get(u'sort[field]', None)
        allowed_sort_fields = [
            'dt_created'
        ]
        if sort_field and sort_field in allowed_sort_fields:
            sort_order = request.GET.get(u'sort[sort]', 'desc')
            if sort_order == 'asc':
                query_set = query_set.order_by(sort_field)
            else:
                query_set = query_set.order_by('-'+sort_field)
        else:
            # Сортировка по убыванию
            query_set = query_set.order_by('-dt_created')

        """Пагинация"""
        total = query_set.count()
        """Определяем отображаемую страницу и заявки на ней"""
        perpage = int(request.GET.get('pagination[perpage]', 10))  # количество на странице
        pages = int(total / perpage) + 1  # всего страниц
        page = int(request.GET.get('pagination[page]', 1))  # текущая страница
        if page > pages:
            page = 1
        first_record = (page - 1) * perpage  # с какой записи брать
        last_record = first_record + perpage  # и по какую
        query_set = query_set[first_record:last_record]

        ref_data = dict()
        ref_data['meta'] = {
            'page': page,
            'pages': pages,
            'perpage': perpage,
            'total': total
        }
        ref_data['data'] = ClaimAttachSerializer2(query_set, many=True).data
        return Response(ref_data)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def api_get_claim(request):
    """API endpoint для получения претензии
    принимает параметры:
    claim_id типа int (1)
    возвращает список job_history [{'id':, 'job':, 'start':, 'end':}]
    """
    # Доступные страницы
    page_codes = ['claim', 'hq_claim', 'promo_claim', 'broker_claim']

    if request.method == 'GET':
        """Получаем claim_id из запроса и фильтруем queryset на основе claim"""
        claim_id = request.GET.get('claim_id', None)

        # Если не передали claim_id
        if not claim_id:
            return HttpResponseBadRequest("No parameters")

        # Если передали claim_id
        try:
            claim_id = int(claim_id)
            claim = ClaimRequest.objects.filter(id=claim_id).first()
        except:
            return HttpResponseBadRequest("Bad parameters")

        if not claim:
            return HttpResponseBadRequest("No claim")

        """Проверка прав доступа"""
        if not check_unit_permission_by_user(request.user, [claim.agency, claim.organization], page_codes, 'read'):
            return HttpResponseBadRequest("No permission")

        # Запрос на список файлов по претензии
        attachments = ClaimAttach.objects.filter(claim=claim, message__isnull=True).order_by('-dt_created')
        if attachments:
            attachments_list = []
            for attachment in attachments:
                attachments_list.append(attachment)
            claim.attachments = attachments_list
        response = ClaimSerializer(claim).data
        return Response(response)


@login_required
@api_view(['GET'])
def api_get_claim_cities(request):
    """API endpoint для получения городов претензии
    принимает параметры:
    headquater_id типа int (1)
    возвращает список
    """
    page_codes = ['claim_frame', 'hq_claim']

    if request.method == 'GET':
        """Получаем headquater_id из запроса и фильтруем queryset на основе headquater"""
        headquater_id = request.GET.get('headquater_id', None)

        # Если не передали headquater_id
        if not headquater_id:
            return HttpResponseBadRequest("No parameters")

        # Если передали headquater_id
        try:
            headquater_id = int(headquater_id)
            headquater = Headquater.objects.filter(id=headquater_id).first()
        except:
            return HttpResponseBadRequest("Bad parameters")

        if not headquater:
            return HttpResponseBadRequest("No headquater")

        """Проверка прав доступа"""
        # Базовая организация компании на которую заданы права
        base_org = get_client_base_org(headquater)
        if not base_org:
            return HttpResponseBadRequest("No base org for headquater")

        # Проверка прав доступа
        if not check_unit_permission_by_user(request.user, base_org, page_codes, 'read'):
            return HttpResponseBadRequest("No permission")

        headquater_cities = Organization.objects.filter(headquater=headquater, kind='city'). \
            annotate(text=F('name')).values('id', 'text')
        response = dict()
        response['city_list'] = OrganizationSerializer4(headquater_cities, many=True).data
        return Response(response)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def api_get_claim_stores_agencies_types(request):
    """API endpoint для получения типов, организаций и агентств в городе для претензии
    принимает параметры:
    city_id типа int (1)
    возвращает список
    """
    # Доступные страницы
    page_codes = ['claim_frame', 'hq_claim']

    if request.method == 'GET':
        """Получаем city_id из запроса и фильтруем queryset на основе city"""
        city_id = request.GET.get('city_id', None)
        orgunit_id = request.GET.get('orgunit_id', None)

        # Если не передали city_id
        if not city_id:
            return HttpResponseBadRequest("No parameters")

        # Если передали city_id
        try:
            orgunit_city_id = int(city_id)
            orgunit_city = Organization.objects.filter(id=orgunit_city_id, kind='city', parent__isnull=False).first()
        except:
            return HttpResponseBadRequest("Bad parameters")

        if not orgunit_city:
            return HttpResponseBadRequest("No city")

        """Проверка прав доступа"""
        if not check_unit_permission_by_user(request.user, orgunit_city, page_codes, 'read'):
            return HttpResponseBadRequest("No permission")

        headquater_stores = Organization.objects.filter(parent=orgunit_city, kind='store'). \
            annotate(text=F('name')).values('id', 'text')

        # Формирование ответа

        claim_types_list = ClaimType.objects.all().annotate(text=F('name')).values('id', 'text')

        response = dict()
        response['claim_types'] = ClaimTypeSerializer2(claim_types_list, many=True).data
        response['orgunit_list'] = OrganizationSerializer4(headquater_stores, many=True).data

        if not orgunit_id:
            return Response(response)

        # Если передали orgunit_id
        try:
            orgunit_id = int(orgunit_id)
            orgunit = Organization.objects.filter(id=orgunit_id, kind='store', parent=orgunit_city).first()
        except:
            return HttpResponseBadRequest("Bad parameters")

        if not orgunit:
            return HttpResponseBadRequest("No orgunit")

        orgunit_city_agencies = OrgLink.objects.filter(organization=orgunit). \
            order_by('agency_id').distinct('agency_id').values_list('agency_id', flat=True)

        party_agency_list = list()
        for party in PARTY_CHOICES:
            if party[0] == 'client':
                continue
            agency_list = Agency.objects.filter(id__in=orgunit_city_agencies, headquater__party=party[0]). \
                annotate(text=F('name')).values('id', 'text')
            if agency_list.exists():
                party_agency_list.append({
                    'text': party[1],
                    'children': AgencySerializer2(agency_list, many=True).data
                })

        response['agency_list'] = party_agency_list
        return Response(response)


@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated, ))
def api_create_claim(request):
    """API endpoint для создания претензий"""
    page_codes = ['claim_frame', 'hq_claim']

    # GET метод используется для получения списка типов претензий и агентств из справочника
    if request.method == 'GET':
        # Типы претензий
        claim_types_list = ClaimType.objects.all().annotate(text=F('name')).values('id', 'text')
        serialized = ClaimTypeSerializer2(claim_types_list, many=True)

        # Если передан headquter (передается обязательно)
        headquater_code = request.GET.get('headquater_code', None)

        # Если не передали headquater
        if not headquater_code:
            return HttpResponseBadRequest("No parameters")

        headquater = Headquater.objects.filter(code=headquater_code).first()

        # Если не нашли headquater
        if not headquater:
            return HttpResponseBadRequest("No headquater")

        """Получаем orgunit_code из запроса и фильтруем queryset на основе orgunit_code"""
        orgunit_code = request.GET.get('orgunit_code', None)
        if not orgunit_code:
            return HttpResponseBadRequest("No parameters")

        orgunit = Organization.objects.filter(headquater=headquater,
                                              kind='store',
                                              code=orgunit_code,
                                              parent__isnull=False). \
            annotate(text=F('name')).first()
        if not orgunit:
            return HttpResponseBadRequest("No orgunit")

        """Проверка прав доступа"""
        if not check_unit_permission_by_user(request.user, orgunit, page_codes, 'read'):
            return HttpResponseBadRequest("No permission")

        orgunit_city_agencies = OrgLink.objects.filter(organization=orgunit). \
            order_by('agency_id').distinct('agency_id').values_list('agency_id', flat=True)

        party_agency_list = list()
        for party in PARTY_CHOICES:
            if party[0] == 'client':
                continue
            agency_list = Agency.objects.filter(id__in=orgunit_city_agencies, headquater__party=party[0]). \
                annotate(text=F('name')).values('id', 'text')
            if agency_list.exists():
                party_agency_list.append({
                    'text': party[1],
                    'children': AgencySerializer2(agency_list, many=True).data
                })

        serialized3 = OrganizationSerializer4(orgunit, many=False)
        response = dict()
        response['guid'] = str(uuid.uuid4())
        response['claim_types'] = serialized.data
        response['agency_list'] = party_agency_list
        response['orgunit'] = serialized3.data
        return Response(response)

    # POST метод используется для создания претензий
    elif request.method == 'POST':
        serializer = ClaimSerializer(data=request.data)

        if serializer.is_valid():
            if 'guid' in request.data:
                claim = ClaimRequest.objects.filter(guid=request.data['guid']).first()
                # Если нашли с таким guid
                if claim:
                    return HttpResponseBadRequest("Claim GUID duplicate")

            if 'organization_id' in request.data:
                organization = Organization.objects.filter(id=request.data['organization_id']).first()
                # Если не нашли с таким id
                if not organization:
                    return HttpResponseBadRequest("No organization with such id")

                # Проверка прав доступа
                if not check_unit_permission_by_user(request.user, organization, page_codes, 'write'):
                    return HttpResponseBadRequest("No permission")
                serializer.validated_data['headquater'] = organization.headquater

            if 'agency_id' in request.data:
                agency = Agency.objects.filter(id=request.data['agency_id']).first()
                # Если не нашли с таким id
                if not agency:
                    return HttpResponseBadRequest("No agency with such id")

                # Проверка прав доступа (что клиент имеет доступ к агентству)
                orglink = OrgLink.objects.filter(agency=agency, headquater=organization.headquater.id).first()
                if not orglink:
                    return HttpResponseBadRequest("No permission")

            # Если не передан user_name
            if 'user_name' not in request.data:
                serializer.validated_data['user_name'] = request.user.first_name + ' ' + request.user.last_name

            # Если передан claim_id
            if 'claim_id' in request.data:
                claim = ClaimRequest.objects.filter(id=request.data['claim_id']).first()
                # Если не нашли с таким id
                if not claim:
                    return HttpResponseBadRequest("No claim with such id")
                # Если нашли c id
                else:
                    serializer.update(claim, serializer.validated_data)
                    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
            # Если не передан id, создаем
            else:
                #max_number = ClaimRequest.objects.filter(headquater=serializer.validated_data['headquater']). \
                #    aggregate(max_number=Max('number'))['max_number']
                #if not max_number:
                #    max_number = 0
                #serializer.validated_data['number'] = max_number + 1
                # Установка статуса
                status_code = ClaimStatus.objects.filter(code='wait').first()
                if status:
                    serializer.validated_data['status_id'] = status_code.id
                try:
                    claim = serializer.save()
                except IntegrityError:
                    return HttpResponseBadRequest("Claim GUID duplicate")

                # Создаем и отправляем уведомления о новой претензии
                make_notify_data(claim, 'agency', 'create_claim_template')
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def api_create_claim_message(request):
    """API endpoint для создания сообщений к претензии"""
    page_codes = ['claim_frame', 'claim', 'hq_claim', 'promo_claim', 'broker_claim']

    # POST метод используется для создания сообщений
    serializer = ClaimMessageSerializer(data=request.data)

    if serializer.is_valid():
        # Если передан claim_id
        if 'claim_id' in request.data:
            claim = ClaimRequest.objects.filter(id=request.data['claim_id']).first()
            # Если не нашли с таким id
            if not claim:
                return HttpResponseBadRequest("No claim with such id")

            # Проверка прав доступа
            if not check_unit_permission_by_user(request.user, [claim.agency, claim.organization], page_codes, 'write'):
                return HttpResponseBadRequest("No permission")

        # Если передан message_id
        if 'message_id' in request.data:
            message = ClaimMessage.objects.filter(id=request.data['message_id']).first()
            # Если не нашли с таким id
            if not message:
                return HttpResponseBadRequest("No claim message with such id")
            # Если нашли c id
            else:
                serializer.update(message, serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        # Если не передан id, создаем
        else:
            message = serializer.save()
            # Устанавливаем дату обновления в претензии
            ClaimRequest.objects.filter(id=message.claim_id). \
                update(dt_updated=message.dt_created)
            # Создаем и отправляем уведомления о новом сообщении
            if message.party == 'client':
                make_notify_data(message, 'agency', 'msg_headquarter_template')
            else:
                make_notify_data(message, 'client', 'msg_agency_template')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def api_create_claim_attachment(request):
    """API endpoint для отправки вложенных файлов"""
    page_codes = ['claim_frame', 'claim', 'hq_claim', 'promo_claim', 'broker_claim']

    serializer = AttachmentUploadSerializer(data=request.data)

    if serializer.is_valid():
        # Если передан claim_id
        if 'claim_id' in request.data:
            claim = ClaimRequest.objects.filter(id=request.data['claim_id']).first()
            # Если не нашли с таким id
            if not claim:
                return HttpResponseBadRequest("No claim with such id")

            # Проверка прав доступа
            if not check_unit_permission_by_user(request.user, [claim.agency, claim.organization], page_codes, 'write'):
                return HttpResponseBadRequest("No permission")

        # Если передан message_id
        if 'message_id' in request.data:
            message = ClaimMessage.objects.filter(id=request.data['message_id']).first()
            # Если не нашли с таким id
            if not message:
                return HttpResponseBadRequest("No message with such id")

            # Проверка прав доступа
            if not check_unit_permission_by_user(request.user, [message.claim.agency, message.claim.organization], page_codes, 'write'):
                return HttpResponseBadRequest("No permission")
            serializer.validated_data['claim'] = message.claim

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def api_set_claim_action(request):
    """API endpoint для смены статуса претензии"""
    page_codes = ['claim_frame', 'claim', 'hq_claim', 'promo_claim', 'broker_claim']

    # Если передан claim_id
    if 'claim_id' in request.data:
        claim = ClaimRequest.objects.filter(id=request.data['claim_id']).first()
        # Если не нашли с таким id
        if not claim:
            return HttpResponseBadRequest("No claim with such id")
    else:
        return HttpResponseBadRequest("No claim id")

    # Проверка прав доступа
    if not check_unit_permission_by_user(request.user, [claim.agency, claim.organization], page_codes, 'write'):
        return HttpResponseBadRequest("No permission")

    # Если передан action
    if 'action' in request.data:
        action = ClaimAction.objects.filter(code=request.data['action']).first()
        # Если не нашли с таким кодом
        if not action:
            return HttpResponseBadRequest("No action code")

        # Если должен быть комментарий
        comment = ''
        if action.need_comment:
            if 'comment' not in request.data or request.data['comment'] == '':
                return HttpResponseBadRequest("No comment supplied")
            comment = request.data['comment']

    else:
        return HttpResponseBadRequest("No action")

    # Если не передан user_name
    if 'user_name' not in request.data or request.data['user_name'] == '':
        user_name = request.user.get_full_name()
    else:
        user_name = request.data['user_name']

    # Обновление статуса
    # TODO Проверка кому доступны какие действия

    if action.code == 'accept':
        status_code = 'accept'
        party = 'agency'
        make_notify_data(claim, 'client', 'accept_claim_template')
    elif action.code == 'reject':
        status_code = 'reject'
        party = 'agency'
        make_notify_data(claim, 'client', 'reject_claim_template')
    elif action.code == 'close':
        status_code = 'closed'
        party = 'client'
        make_notify_data(claim, 'agency', 'close_claim_template')
    else:
        status_code = 'wait'
        party = 'client'
        make_notify_data(claim, 'agency', 'create_claim_template')

    status_new = ClaimStatus.objects.filter(code=status_code).first()

    # Ответ
    message = dict()
    message['type'] = 'success'
    message['claim'] = claim.id
    if claim.dt_status_changed:
        message['dt_status_changed'] = claim.dt_status_changed.isoformat()

    if claim.status:
        status_old = claim.status
        message.update({'status_old': status_old.name})
        # Если не было изменения статуса
        if claim.status == status_new:
            message.update({'type': 'info'})
            return Response(message, status=status.HTTP_304_NOT_MODIFIED)
    else:
        status_old = None

    claim.dt_status_changed = timezone.now()
    claim.status = status_new
    claim.save(update_fields=['dt_status_changed', 'status'])

    # Добавление информации о смене статуса
    ClaimHistory.objects.create(claim=claim,
                                dt_created=claim.dt_status_changed,
                                state_from=status_old,
                                state_to=claim.status,
                                party=party,
                                comment=comment,
                                user_name=user_name)

    message.update({'status_new': claim.status.name})
    message.update({'dt_status_changed': claim.dt_status_changed.isoformat()})

    # Создаем и отправляем уведомления о смене статуса претензии
    # TODO отправка уведомлений о смене статуса
    make_notify_data(claim, 'agency', 'status_claim_template')
    make_notify_data(claim, 'client', 'status_claim_template')
    return Response(message, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def api_get_headquater_documents(request):
    """API endpoint для получения документов по клиенту
    принимает параметры:
    headquater_code типа str
    возвращает список документов
    """
    page_codes = ['claim_frame']

    """Получаем headquater_code из запроса"""
    headquater_code = request.GET.get('headquater_code', None)

    # Если не передали headquater_code
    if not headquater_code:
        return HttpResponseBadRequest("No headquater code")

    headquater = Headquater.objects.filter(code=headquater_code).first()
    if not headquater:
        return HttpResponseBadRequest("No headquater with such code")

    """Проверка прав доступа"""
    # Базовая организация компании на которую заданы права
    base_org = get_client_base_org(headquater)
    if not base_org:
        return HttpResponseBadRequest("No base org for headquater")

    # Проверка прав доступа
    if not check_unit_permission_by_user(request.user, base_org, page_codes, 'read'):
        return HttpResponseBadRequest("No permission")

    documents = Document.objects.filter(headquater=headquater).order_by('-dt_created')
    response = DocumentSerializer(documents, many=True).data
    return Response(response)
