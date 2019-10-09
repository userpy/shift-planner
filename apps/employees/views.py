#
# Copyright 2018 ООО «Верме»
#
# Файл представлений сотрудников
#
# Для работы нужен permission/methods.py, который содержит проверку прав доступа;
# rest_framework, outsource/serializers.py, который содержит serializers для методов api
#

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import json

#
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.outsource.serializers import HeadquaterSerializer, JobSerializer, OrganizationSerializer3
from apps.permission.models import AccessProfile
#
import datetime
from django.db.models import Q, F
from django.utils import timezone
from .models import *
from .methods import *
from .serializers import *

from apps.lib.methods import *
from apps.outsource.methods import open_headquarter, open_agency, open_organization, clients_by_agency, \
    cities_by_agency, open_orgunit

from apps.permission.decorators import check_page_permission_by_user
from apps.permission.methods import check_struct_access_to_page, available_headquarters
from apps.violations.methods import make_violations_data, open_violation_level

from xlsexport.methods import get_report_by_code

""" ************************************* СПИСОК СОТРУДНИКОВ ************************************** """


@login_required
@check_page_permission_by_user
def employees_list(request, **context):
    """Список сотрудников для менеджера аутсорсинг агентства"""
    # TODO счетчики
    context.update({"claim_count": 0, "request_count": 0,
                    "is_verme_docs_enabled": check_verme_docs()[0],
                    "verme_docs_url": check_verme_docs()[1]})
    return render(request, "employees/employees_list.html", context)


@login_required
@check_page_permission_by_user
def promo_employees_list(request, **context):
    """Список сотрудников для менеджера промо агентства"""
    context.update({"is_verme_docs_enabled": check_verme_docs()[0],
                    "verme_docs_url": check_verme_docs()[1]})
    return render(request, "employees/employees_list.html", context)


@login_required
@check_page_permission_by_user
def broker_employees_list(request, **context):
    """Список сотрудников для кредитного брокера"""
    context.update({"is_verme_docs_enabled": check_verme_docs()[0],
                    "verme_docs_url": check_verme_docs()[1]})
    return render(request, "employees/employees_list.html", context)


@login_required
@check_page_permission_by_user
def hq_employees_list(request, **context):
    """Список сотрудников для сотрудника клиента"""
    context.update({"is_verme_docs_enabled": check_verme_docs()[0],
                    "verme_docs_url": check_verme_docs()[1]})
    return render(request, "employees/hq_employees_list.html", context)


@login_required
@api_view(['GET'])
def api_employees_list(request):
    """API endpoint для получения списка сотрудников агентства на дату"""
    page_codes = ['employees_list', 'promo_employees_list', 'broker_employees_list', 'hq_employees_list']
    current_user = request.user

    if request.method == 'GET':
        """Определяем орг. единицу"""
        unit_headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
        if not unit_headquarter:
            return make_error_response('Undefined: orgunit')

        """ Проверка прав доступа """
        if not check_struct_access_to_page(current_user, unit_headquarter, unit, page_codes, 'read'):
            return make_error_response('AccessDenied')

        date = request.GET.get('date', None)
        if not date:
            date = request.GET.get('month', None)
        if not date:
            date = timezone.now().date()

        """Определяем агентство"""
        agency = open_agency(request.GET.get('agency_id', None))

        """Определяем компанию клиента"""
        headquarter = open_headquarter(request.GET.get('headquarter_id', None))

        """Определяем компанию агентства"""
        aheadquarter = open_headquarter(request.GET.get('aheadquarter_id', None))

        """Определяем нарушение"""
        try:
            violations = json.loads(request.GET.get('violation_ids', '[]'))
        except json.JSONDecodeError:
            violations = []

        """Формирование queryset сотрудников"""
        query_set = make_emp_queryset(unit_headquarter, unit, date)

        """Ограничиваем сотрудников по состоянию"""
        state = request.GET.get('state', 'all')
        if state == 'active':
            if unit_headquarter.party == 'client':
                orghistory_ids = OrgHistory.objects.filter(headquater=unit_headquarter)
                if unit:
                    orghistory_ids = orghistory_ids.filter(Q(organziation=unit) | Q(organization__parent=unit))
                orghistory_ids = orghistory_ids.filter(
                    Q(start__lte=date, end__gte=date) | Q(start__lte=date, end__isnull=True)). \
                    order_by('agency_employee_id').distinct('agency_employee_id'). \
                    values_list('agency_employee_id', flat=True)
                query_set = query_set.filter(id__in=orghistory_ids)
            else:
                query_set = query_set.filter(
                    Q(receipt__lte=date, dismissal__gt=date) | Q(receipt__lte=date, dismissal__isnull=True))
        elif state == 'dismissed':
            if unit_headquarter.party == 'client':
                orghistory_ids = OrgHistory.objects.filter(headquater=unit_headquarter)
                if unit:
                    orghistory_ids = orghistory_ids.filter(Q(organziation=unit) | Q(organization__parent=unit))
                ended_orghistory_ids = orghistory_ids.filter(end__lte=date). \
                    order_by('agency_employee_id').distinct('agency_employee_id'). \
                    values_list('agency_employee_id', flat=True)
                active_orghistory_ids = orghistory_ids.filter(Q(end__isnull=True) |
                                                              Q(end__gte=date)). \
                    order_by('agency_employee_id').distinct('agency_employee_id'). \
                    values_list('agency_employee_id', flat=True)
                result_orghistory_ids = list(set(ended_orghistory_ids) - set(active_orghistory_ids))
                query_set = query_set.filter(id__in=result_orghistory_ids)
            else:
                query_set = query_set.filter(dismissal__lte=date)

        """Ограничиваем сотрудников по клиенту"""
        if headquarter:
            # TODO убедиться, что дата уже не нужна, и убрать ее
            query_set = query_set.filter(id__in=make_headquarter_emp_ids(date, headquarter))

        """Ограничиваем сотрудников по компании агентства"""
        if aheadquarter:
            aheadquater_agencies = agency_ids_by_aheadquarter(aheadquarter)
            query_set = query_set.filter(agency_id__in=aheadquater_agencies)

        """Ограничиваем сотрудников по агентству"""
        if agency:
            query_set = query_set.filter(agency=agency)

        """Формирование списка агентств для фильтра"""
        agency_queryset = query_set.order_by('agency_id').distinct('agency_id').values('agency_id', 'agency__name'). \
            annotate(id=F('agency_id'), text=F('agency__name')).values('id', 'text')

        """Поиск"""
        query_set = make_search(query_set, request.GET.get(u'datatable[query][generalSearch]', None))

        """Сортировка"""
        sort_fields = ['surname', 'firstname', 'patronymic', 'number']
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
            return get_report_by_code(request.GET.get('xlsexport_code', None), query_set)

        # Выгрузка в Excel
        medical_export = request.GET.get('medical_export', None)
        if medical_export:
            return get_medical_docs(request, query_set, page_codes, page_codes, unit_headquarter)

        """Пагинация"""
        emp_query_set, meta = make_pagination(query_set, request.GET.get('pagination[page]', 1),
                                              request.GET.get('pagination[perpage]', 10))

        """Для каждого сотрудника"""
        agency_employee_list = []
        for q in emp_query_set:
            agency_employee_list.append(make_emp_data(page_codes, q, date, unit_headquarter))

        ref_data = dict()
        ref_data['meta'] = meta
        ref_data['data'] = agency_employee_list
        ref_data['violations_list'] = make_violations_data(page_codes, unit_headquarter.party)
        ref_data['agency_list'] = list(agency_queryset)

        return Response(ref_data)


class ApiEmployeesListView(APIView, ):
    """API endpoint для получения списка сотрудников агентства на дату"""
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)
    page_codes = ['employees_list', 'promo_employees_list', 'broker_employees_list', 'hq_employees_list']

    def get(self, request):
        current_user = request.user
        serializer = AgencyEmployeeListRequestSerializer(data=request.GET)

        serializer.is_valid(raise_exception=True)

        """Определяем орг. единицу"""
        unit_headquarter, unit = open_orgunit(serializer.validated_data.get('orgunit'))
        if not unit_headquarter:
            raise serializers.ValidationError('orgunit')

        """ Проверка прав доступа """
        if not check_struct_access_to_page(current_user, unit_headquarter, unit, self.page_codes, 'read'):
            return make_error_response('AccessDenied')

        date = serializer.validated_data.get('date')
        if not date:
            date = serializer.validated_data.get('month')
        if not date:
            date = timezone.now().date()

        """Определяем агентство"""
        agency = open_agency(serializer.validated_data.get('agency_id'))

        """Определяем компанию клиента"""
        headquarter = open_headquarter(serializer.validated_data.get('headquarter_id'))

        """Определяем компанию агентства"""
        aheadquarter = open_headquarter(serializer.validated_data.get('aheadquarter_id'))

        """Определяем нарушение"""
        try:
            violations = json.loads(serializer.validated_data.get('violation_ids'))
        except:
            violations = []
        """Формирование queryset сотрудников"""
        query_set = make_emp_queryset(unit_headquarter, unit, date)

        """Ограничиваем сотрудников по состоянию"""
        state = serializer.validated_data.get('state', 'all')
        if state == 'active':
            if unit_headquarter.party == 'client':
                orghistory_ids = OrgHistory.objects.filter(headquater=unit_headquarter)
                if unit:
                    orghistory_ids = orghistory_ids.filter(Q(organziation=unit) | Q(organization__parent=unit))
                orghistory_ids = orghistory_ids.filter(
                    Q(start__lte=date, end__gte=date) | Q(start__lte=date, end__isnull=True)). \
                    order_by('agency_employee_id').distinct('agency_employee_id'). \
                    values_list('agency_employee_id', flat=True)
                query_set = query_set.filter(id__in=orghistory_ids)
            else:
                query_set = query_set.filter(
                    Q(receipt__lte=date, dismissal__gt=date) | Q(receipt__lte=date, dismissal__isnull=True))
        elif state == 'dismissed':
            if unit_headquarter.party == 'client':
                orghistory_ids = OrgHistory.objects.filter(headquater=unit_headquarter)
                if unit:
                    orghistory_ids = orghistory_ids.filter(Q(organziation=unit) | Q(organization__parent=unit))
                ended_orghistory_ids = orghistory_ids.filter(end__lte=date). \
                    order_by('agency_employee_id').distinct('agency_employee_id'). \
                    values_list('agency_employee_id', flat=True)
                active_orghistory_ids = orghistory_ids.filter(Q(end__isnull=True) |
                                                              Q(end__gte=date)). \
                    order_by('agency_employee_id').distinct('agency_employee_id'). \
                    values_list('agency_employee_id', flat=True)
                result_orghistory_ids = list(set(ended_orghistory_ids) - set(active_orghistory_ids))
                query_set = query_set.filter(id__in=result_orghistory_ids)
            else:
                query_set = query_set.filter(dismissal__lte=date)
        """Ограничиваем сотрудников по клиенту"""
        if headquarter:
            # TODO убедиться, что дата уже не нужна, и убрать ее
            query_set = query_set.filter(id__in=make_headquarter_emp_ids(date, headquarter))

        """Ограничиваем сотрудников по компании агентства"""
        if aheadquarter:
            aheadquater_agencies = agency_ids_by_aheadquarter(aheadquarter)
            query_set = query_set.filter(agency_id__in=aheadquater_agencies)

        """Ограничиваем сотрудников по агентству"""
        if agency:
            query_set = query_set.filter(agency=agency)
        query_set = AgencyEmployee.objects.filter(id__in=query_set.values_list('id', flat=True))
        """Формирование списка агентств для фильтра"""
        agency_queryset = query_set.order_by('agency_id').distinct('agency_id').values('agency_id', 'agency__name'). \
            annotate(id=F('agency_id'), text=F('agency__name')).values('id', 'text')

        """Поиск"""
        query_set = make_search(query_set, request.GET.get(u'datatable[query][generalSearch]', None))

        """Сортировка"""
        sort_fields = ['surname', 'firstname', 'patronymic', 'number']
        query_set = make_sort(query_set, sort_fields, request.GET.get(u'sort[field]', None),
                              request.GET.get(u'sort[sort]', 'desc'))

        """Фильтрация по нарушениям"""
        if violations:
            for violation_id in violations:
                violation = open_violation_level(violation_id)
                if violation:
                    query_set = violation.check_queryset(query_set, date)

        # Выгрузка в Excel
        export = serializer.validated_data.get('xlsexport')
        if export:
            return get_report_by_code(serializer.validated_data.get('xlsexport_code'), query_set)

        # Выгрузка в Excel
        medical_export = serializer.validated_data.get('medical_export')
        if medical_export:
            return get_medical_docs(request, query_set, self.page_codes, self.page_codes, unit_headquarter)

        """Пагинация"""
        emp_query_set, meta = make_pagination(query_set, request.GET.get('pagination[page]', 1),
                                              request.GET.get('pagination[perpage]', 10))

        """Для каждого сотрудника"""
        agency_employee_list = []
        for q in emp_query_set:
            agency_employee_list.append(make_emp_data(self.page_codes, q, date, unit_headquarter))

        ref_data = dict()
        ref_data['meta'] = meta
        ref_data['data'] = agency_employee_list
        ref_data['violations_list'] = make_violations_data(self.page_codes, unit_headquarter.party)
        ref_data['agency_list'] = list(agency_queryset)

        return Response(AgencyEmployeeListResponseSerializer(ref_data, many=False).data)


""" ************************************* КАРТОЧКА СОТРУДНИКА ************************************** """


@login_required
@check_page_permission_by_user
def create_employee(request, **context):
    # Параметры отображения

    context.update({"is_org_select_disabled": True,
                    "is_verme_docs_enabled": check_verme_docs()[0],
                    "verme_docs_url": check_verme_docs()[1],
                    "verme_docs_login": check_verme_docs()[2]})
    # TODO счетчики
    context.update({"claim_count": 0, "request_count": 0})
    return render(request, "employees/employee_profile.html", context)


@login_required
@check_page_permission_by_user
def edit_employee(request, employee_id, **context):
    # Параметры отображения
    employee = open_employee(employee_id)
    if not employee:
        return make_error_response("Сотрудник не найден")
    try:
        is_transition_enabled = True if Config.objects.get(headquater=employee.agency.headquater,
                                                           key='is_employee_transition') else False
        if Agency.objects.filter(headquater=employee.agency.headquater).count() < 2:
            # есть ли выбор
            is_transition_enabled = False
        else:
            is_transition_enabled = False
            aps = AccessProfile.objects.filter(user=request.user, headquater=employee.agency.headquater)
            for ap in aps:
                print(ap.unit.parent)
                if not ap.unit.parent:
                    is_transition_enabled = True
                    break
            if request.user.is_staff:
                is_transition_enabled = True

    except Config.DoesNotExist:
        is_transition_enabled = False

    context.update({
        "is_org_select_disabled": True,
        "is_verme_docs_enabled": check_verme_docs()[0],
        "verme_docs_url": check_verme_docs()[1],
        "verme_docs_login": check_verme_docs()[2],
        "employee_id": employee.id,
        "disabled": "disabled",
        "is_transition_enabled": is_transition_enabled
    })

    # TODO счетчики
    context.update({"claim_count": 0, "request_count": 0})

    # Запускаем отрисовку шаблона
    return render(request, "employees/employee_profile.html", context)


@login_required
@api_view(['GET', 'POST', 'DELETE'])
def api_employee(request):
    """
    API endpoint, работает в следующих трех режимах:
    - GET - вывод информации о сотруднике
    - POST - создание / редактирование одной или нескольких сотрудников
    - DELETE - удаление сотрудника
    """
    current_user = request.user
    client_pages = ['hq_edit_employee']
    agency_pages = ['edit_employee', 'promo_edit_employee', 'broker_edit_employee']

    # GET - Получение данных по выбранному сотруднику
    if request.method == 'GET':
        # Поиск объекта сотрудника
        employee = open_employee(request.GET.get('agency_employee_id', None))
        if not employee:
            return make_error_response('Undefined: agency_employee_id')

        # ПРОВЕРКА ПРАВ ДОСТУПА
        has_access = False
        # - проврка доступа для сотрудника агентства
        if check_struct_access_to_page(current_user, employee.agency.headquater, employee.agency, agency_pages, 'read'):
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

        employee.violations = check_violation_rules_by_date(client_pages + agency_pages,
                                                            employee.agency.headquater,
                                                            employee)

        # Формируем ответное сообщение
        return Response({"employee": AgencyEmployeeReadSerializer(employee, many=False).data,
                         "cur_jobs": JobSerializer(employee_jobs(employee), many=True).data})

    # POST - Создание, редактирование
    elif request.method == 'POST':
        # Проверка переданных данных

        serializer = AgencyEmployeeWriteSerializer(data=request.data )
        serializer.current_user = current_user
        serializer.agency_pages = agency_pages
        if not serializer.is_valid():
            errors = serializer.errors
            if not request.data.get('date_of_birth', ''):

                errors.update({'date_of_birth': ["Не заполнена дата рождения"]})
            if not request.data.get('receipt', ''):

                errors.update({'receipt': ["Не заполнена дата приема"]})

            return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        # Параметр запроса - ID сотрудника
        employee = None
        if 'agency_employee_id' in request.data:

            employee = open_employee(request.data['agency_employee_id'])
        # Параметр запроса - Агентство
        if 'agency_id' not in request.data:

            return make_error_response("Undefined: agency_id")
        agency = open_agency(request.data['agency_id'])

        # ПРОВЕРКА ПРАВ ДОСТУПА
        if not check_struct_access_to_page(current_user, agency.headquater, agency, agency_pages, 'write'):

            return make_error_response("AccessDenied")
        elif employee and employee.agency != agency:

            return make_error_response("AccessDenied: employee.agency != agency")

        # Редактирование существующего сотрудника
        if employee:

            serializer.update(employee, serializer.validated_data, current_user)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

        # Создание нового сотрудника
        else:

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    # TODO - Требуется проработать, что делать со сменами, событиями и другими связанными объектами
    '''
    # DELETE - Удаление сотрудника
    elif request.method == 'DELETE':
        employee_ids = json.loads(request.data['agency_employee_ids']) if 'agency_employee_ids' in request.data else []
        # Удаляем выбранных сотрудников, если такой объект существует и у пользователя есть необходимые права доступа
        for employee_id in employee_ids:
            employee = open_employee(employee_id)
            if employee and check_struct_access_to_page(current_user, employee.agency.headquater, employee.agency, agency_page_codes, "write"):
                employee.delete()
            else:
                return make_error_response('AccessDenied')
        return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)
    '''
    # Неизвестный метод
    return make_error_response('UnknownError')


""" ************************************ ПРИКРЕПЛЕНИЕ СОТРУДНИКОВ ************************************* """


@login_required
@api_view(['GET'])
def api_get_headquaters_organizations(request):
    """Возвращает список организаций клиента, с которыми может работать выбранное агентство"""
    current_user = request.user
    page_codes = ['promo_edit_employee', 'edit_employee', 'employees_list', 'promo_employees_list',
                  'broker_edit_employee', 'broker_employees_list']

    # Проверка параметров - агентство
    agency = open_agency(request.GET.get('agency_id', None))
    # Проверка параметров - клиента
    headquarter = open_headquarter(request.GET.get('headquater_id', None))

    # Если не задано агентство, то возвращем список Headquarter типа 'client'. Данный функционал
    # используется в интерфейсе клиента. TODO - выглядит так, что данный вызов не нужен. 
    if not agency:
        headquarters = available_headquarters(current_user, 'client')
        return Response(HeadquaterSerializer(headquarters, many=True).data)
    # Если не задан headquarter, то вовзращаем список клиентов, с которым может работать агентство
    elif not headquarter:
        # Проверка прав доступа
        if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, 'read'):
            return make_error_response("AccessDenied")
        # Формируем список клиентов
        headquaters = clients_by_agency(agency).order_by('name')
        return Response(HeadquaterSerializer(headquaters, many=True).data)
    # В противном случае возвращаем список доступных структурных подразделений клиента
    else:
        # Проверка прав доступа
        if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, 'read'):
            return make_error_response("AccessDenied")
        # Проверяем, что агентство может работать с выбранным клинетом
        headquaters = clients_by_agency(agency)
        if not headquarter in headquaters:
            return make_error_response("Агентство " + agency.name + ' не работает с ' + headquarter.name)
        # Формируем список городов
        organizations = cities_by_agency(agency, headquarter).order_by('name')
        return Response(OrganizationSerializer3(organizations, many=True).data)


@login_required
@api_view(['POST'])
def api_set_employee_recruitment_event(request):
    """ Прикрепление сотрудника агентства к заданному клиенту """
    current_user = request.user
    page_codes = ['promo_edit_employee', 'edit_employee', 'employees_list', 'promo_employees_list',
                  'broker_edit_employee', 'broker_employees_list']

    # Проверка параметров - город (TODO - переделать на прикрепление к клиенту)
    organization = open_organization(request.data['organization_id'])
    if not organization:
        return make_error_response("Undefined: organization_id")
    # Проверка параметров  - дата приема
    if 'recruitment_date' not in request.data:
        return make_error_response("Undefined: recruitment_date")
    recruitment_date = datetime.datetime.strptime(request.data['recruitment_date'], "%Y-%m-%d").date()
    if (recruitment_date - datetime.datetime.now().date()).days > 30:
        return make_error_response("Текущими настройками запрещен прием сотрудников датой на 30 и более дней вперед")
    # Проверка параметров - список сотрудников
    if not 'employee_list' in request.data:
        return make_error_response("Undefined: employee_list")
    employee_list = json.loads(request.data['employee_list'])

    # Последовательно обходим переданных сотрудников и приркепляем к клиенту
    for employee_id in employee_list:
        employee = open_employee(employee_id)
        if not employee:
            continue
        # Проверка прав доступа
        agency = employee.agency
        if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, 'write'):
            return make_error_response("AccessDenied: employee - {employee_id}")
        # Принимаем сотрудника на работу
        attach_employee(current_user, employee, recruitment_date, organization)
    # Возвращаем положительный ответ
    return Response("Employees are taken", status=status.HTTP_201_CREATED)


""" ************************************* УВОЛЬНЕНИЕ СОТРУДНИКОВ ************************************** """


@login_required
@api_view(['POST'])
def api_dismiss_employee_from_client(request):
    """ Открепление сотрудника агентства от заданного клиента """
    current_user = request.user
    agency_pages = ['promo_edit_employee', 'edit_employee', 'employees_list', 'promo_employees_list',
                    'broker_edit_employee', 'broker_employees_list']
    client_pages = ['hq_edit_employee', 'hq_employees_list']

    # Проверка параметров - причина увольнения
    if 'dismissal_reason' not in request.data:
        return make_error_response("Не указана причина открепления")
    dismissal_reason = request.data['dismissal_reason']
    # Проверка параметров - дата увольнения
    if 'dismissal_date' not in request.data:
        return make_error_response("Не указана дата открепления")
    dismissal_date = datetime.datetime.strptime(request.data['dismissal_date'], "%Y-%m-%d").date()
    if dismissal_date < timezone.now().date():
        return make_error_response("Не допускается открепление в прошлом периоде")
    # Проверка параметров - компания клиента
    if request.data.get('orgunit', None):
        headquarter, unit = open_orgunit(request.data.get('orgunit', None))
    else:
        headquarter = open_headquarter(request.data['headquater_id'])
        unit = None
    if not headquarter:
        return make_error_response("Не указан клиент")
    if headquarter.party != 'client':
        return make_error_response("Некорректно указана компания клиента")
    # Проверка параметров - список увольняемых сотрудников
    if not 'employee_list' in request.data:
        return make_error_response("Не задан список сотрудников")
    employee_list = json.loads(request.data['employee_list'])
    # Проверка параметров - включение в черный список
    try:
        from distutils.util import strtobool
        blacklist = strtobool(request.POST.get('blacklist', 'false'))
    except:
        blacklist = False
    # Последовательно обходим переданных сотрудников и открепляем от клиентов
    for employee_id in employee_list:
        employee = open_employee(employee_id)
        if not employee:
            continue
        agency = employee.agency
        # Проверка прав доступа
        if check_struct_access_to_page(current_user, headquarter, unit, client_pages, 'write'):
            # Пользователь является менеджером клинета по работе с внешним персоналом
            pass
        elif check_struct_access_to_page(current_user, agency.headquater, agency, agency_pages, 'write'):
            # Пользователь является менеджером аутсорсингового агентства
            pass
        else:
            return make_error_response("AccessDenied: {employee.number}")
        # Откреплям сотрудника
        dismiss_employee(current_user, employee, dismissal_date, dismissal_reason, blacklist, headquarter)
    # Возвращаем положительный ответ
    return Response("Employees are dismissed", status=status.HTTP_201_CREATED)


@login_required
@api_view(['POST'])
def api_dismiss_employee(request):
    """ Увольнение сотрудника из агентства """
    current_user = request.user
    page_codes = ['edit_employee', 'promo_edit_employee', 'broker_edit_employee']

    # Проверка параметров - причина увольнения
    if 'dismissal_reason' not in request.data:
        return make_error_response("Undefined: dismissal_reason")
    dismissal_reason = request.data['dismissal_reason']
    # Проверка параметров - дата увольнения
    if 'dismissal_date' not in request.data:
        return make_error_response("Undefined: dismissal_date")
    dismissal_date = datetime.datetime.strptime(request.data['dismissal_date'], "%Y-%m-%d").date()
    if dismissal_date < timezone.now().date():
        return make_error_response("Dismissal date less then now")
    # Проверка параметров - список увольняемых сотрудников
    if not 'employee_list' in request.data:
        return make_error_response("Undefined: employee_list")
    employee_list = json.loads(request.data['employee_list'])

    # Последовательно обходим переданных сотрудников и открепляем от клиентов
    for employee_id in employee_list:
        employee = open_employee(employee_id)
        if not employee:
            continue
        agency = employee.agency

        # Проверка прав доступа
        if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, 'write'):
            make_error_response("AccessDenied: employee - {employee_id}")

        # Откреплям сотрудника
        dismiss_employee(current_user, employee, dismissal_date, dismissal_reason, False, None)
    # Возвращаем положительный ответ
    return Response("Employees are dismissed", status=status.HTTP_204_NO_CONTENT)


""" ************************************* ДОКУМЕНТЫ СОТРУДНИКА ************************************** """


@login_required
@api_view(['GET'])
def api_doc_types(request):
    """Список видов документов"""
    docs_types = DocType.objects.all()
    return Response(DocTypeSerializer(docs_types, many=True).data)


@login_required
@api_view(['GET'])
def api_get_docs_archive(request):
    """ Возвращает ссылку на архив документов сервиса docs"""
    current_user = request.user
    agency_pages = ['edit_employee', 'promo_edit_employee', 'broker_edit_employee', 'employees_list',
                    'promo_employees_list',
                    'broker_edit_employee', 'broker_employees_list']
    client_pages = ['hq_edit_employee', 'hq_employees_list']

    """Определяем орг. единицу"""
    unit_headquarter, unit = open_orgunit(request.GET.get('orgunit', None))
    if not unit_headquarter:
        return make_error_response('Undefined: orgunit')

    # Список сотрудников
    employee_list = json.loads(request.GET['employee_ids'])

    return get_medical_docs(request, employee_list, agency_pages, client_pages, unit_headquarter)


@login_required
@api_view(['GET'])
def api_employee_docs(request):
    """ Возвращает список документов сотрудника """
    current_user = request.user
    agency_pages = ['edit_employee', 'promo_edit_employee', 'broker_edit_employee']
    client_pages = ['hq_edit_employee']

    # Сотрудник агентства
    employee = open_employee(request.GET.get('agency_employee_id', None))
    if not employee:
        return make_error_response('Undefined: agency_employee_id')

    # ПРОВЕРКА ПРАВ ДОСТУПА
    has_access = False
    # - проврка доступа для сотрудника агентства
    if check_struct_access_to_page(current_user, employee.agency.headquater, employee.agency, agency_pages, 'read'):
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

    # Формируем cписок документов
    query = EmployeeDoc.objects.filter(agency_employee=employee).order_by('-start')
    return Response(EmployeeDocReadSerializer(query, many=True).data)


@login_required
@api_view(['GET', 'POST', 'DELETE'])
def api_employee_doc(request):
    """
    API endpoint, работает в следующих двух режимах:
    - GET - вывод информации о документе
    - POST - создание / редактирование одного или нескольких документов
    - DELETE - удаление документа
    """
    current_user = request.user
    page_codes = ['promo_edit_employee', 'edit_employee', 'broker_edit_employee']

    # GET - Получение данных по выбранному документу
    if request.method == 'GET':
        # Поиск объекта документа
        employee_doc = open_employee_doc(request.GET.get('doc_id', None))
        if not employee_doc:
            return make_error_response('Undefined: doc_id')
        agency = employee_doc.agency_employee.agency
        # ПРОВЕРКА ПРАВ ДОСТУПА
        if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, 'read'):
            return make_error_response('AccessDenied')
        docs_params = make_docs_params(current_user, employee_doc.guid)
        # Формируем ответное сообщение
        return Response({"doc": EmployeeDocReadSerializer(employee_doc, many=False).data,
                         "reqParams": docs_params})

    # POST - Создание, редактирование
    elif request.method == 'POST':
        # Обработка одного элемента
        def process_one_doc(doc_data):
            # Проверка корректности переданных данных
            serializer = EmployeeDocWriteSerializer(data=doc_data)
            if not serializer.is_valid():
                return serializer.errors, None
            # ПРОВЕРКА ПРАВ ДОСТУПА
            agency_employee = serializer.validated_data['agency_employee']
            agency = agency_employee.agency
            if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, "write"):
                return make_error_response('AccessDenied')
            # СОЗДАНИЕ \ РЕДАКТИРОВАНИЕ ДОКУМЕНТА
            employee_doc = open_employee_doc(doc_data.get('doc_id'))
            if employee_doc:
                employee_doc = serializer.update(employee_doc, serializer.validated_data, current_user)
            else:
                employee_doc = serializer.create(serializer.validated_data, current_user)
            return None, employee_doc

        # Сохранение массива данных
        if 'docs' in request.data:
            docs_data = json.loads(request.data['docs'])
            for doc_data in docs_data:
                error, employee_doc = process_one_doc(doc_data)
                if error:
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)
        # Сохранение одного элемента
        else:
            error, employee_doc = process_one_doc(request.data)
            if error:
                return Response(error, status=status.HTTP_400_BAD_REQUEST)

        docs_params = make_docs_params(current_user, employee_doc.guid)
        # Возврат результата
        return Response({"doc": EmployeeDocReadSerializer(employee_doc, many=False).data,
                         "reqParams": docs_params}, status=status.HTTP_201_CREATED)

    # DELETE - Удаление документа
    # в заголовках запроса должен уходить X-CSRFToken
    elif request.method == 'DELETE':
        docs_list = json.loads(request.data['doc_ids']) if 'doc_ids' in request.data else []
        # Если объект существует и у пользователя есть необходимые права доступа, то удаляем
        for doc_id in docs_list:
            employee_doc = open_employee_doc(doc_id)
            if not employee_doc:
                continue
            agency = employee_doc.agency_employee.agency
            if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, "write"):
                return make_error_response("AccessDenied")
            # Удаляем сам объект
            employee_doc.delete()
        return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)

    # Неизвестный метод
    else:
        return make_error_response('UnknownError')


""" ************************************* ДОЛЖНОСТИ СОТРУДНИКА ************************************** """


@login_required
@api_view(['GET'])
def api_job_histories(request):
    """
    Возвращает список назначений должностей сотруднику
    """
    current_user = request.user
    agency_pages = ['edit_employee', 'promo_edit_employee', 'broker_edit_employee']
    client_pages = ['hq_edit_employee']

    # Сотрудник агентства
    employee = open_employee(request.GET.get('agency_employee_id', None))
    if not employee:
        return make_error_response('Undefined: agency_employee_id')

    # ПРОВЕРКА ПРАВ ДОСТУПА
    has_access = False
    # - проврка доступа для сотрудника агентства
    if check_struct_access_to_page(current_user, employee.agency.headquater, employee.agency, agency_pages, 'read'):
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

    # Формируем список должностей
    job_history = JobHistory.objects.filter(agency_employee=employee)
    return Response(JobHistoryReadSerializer(job_history, many=True).data)


@login_required
@api_view(['GET', 'POST', 'DELETE'])
def api_job_history(request):
    """
    API endpoint, работает в следующих трех режимах:
    - GET - вывод информации о функции
    - POST - создание / редактирование одной или нескольких функций
    - DELETE - удаление функции
    """
    current_user = request.user
    page_codes = ['promo_edit_employee', 'edit_employee', 'broker_edit_employee']

    # GET - Получение данных по выбранной функции
    if request.method == 'GET':
        # Поиск объекта назначения функции
        employee_job_history = open_employee_job_history(request.GET.get('job_history_id', None))
        if not employee_job_history:
            return make_error_response('Undefined: job_history_id')
        # ПРОВЕРКА ПРАВ ДОСТУПА
        agency = employee_job_history.agency_employee.agency
        if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, 'read'):
            return make_error_response('AccessDenied')
        # Формируем ответное сообщение
        return Response({"job_history": JobHistoryReadSerializer(employee_job_history, many=False).data})

    # POST - Создание, редактирование
    elif request.method == 'POST':
        # Обработка одного элемента
        def process_one_job_history(job_history_data):
            # Проверка корректности переданных данных
            serializer = JobHistoryWriteSerializer(data=job_history_data)
            if not serializer.is_valid():
                return serializer.errors
            # ПРОВЕРКА ПРАВ ДОСТУПА
            agency_employee = serializer.validated_data['agency_employee']
            agency = agency_employee.agency
            if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, "write"):
                return make_error_response('AccessDenied'), None
            # СОЗДАНИЕ \ РЕДАКТИРОВАНИЕ НАЗНАЧЕНИЯ
            job_history = open_employee_job_history(job_history_data.get('job_history_id', None))
            if job_history:
                job_history = serializer.update(job_history, serializer.validated_data, current_user)
            else:
                job_history = serializer.create(serializer.validated_data, current_user)
            return None

        # Сохранение массива данных
        if 'job_histories' in request.data:
            job_histories_data = json.loads(request.data['job_histories'])
            for job_history_data in job_histories_data:
                error = process_one_job_history(job_history_data)
                if error:
                    return Response(error, status=status.HTTP_400_BAD_REQUEST)
        # Сохранение одного элемента
        else:
            error = process_one_job_history(request.data)
            if error:
                return Response(error, status=status.HTTP_400_BAD_REQUEST)
        # Возврат результата
        return Response('Successfully created', status=status.HTTP_201_CREATED)

    # DELETE - Удаление документа
    elif request.method == 'DELETE':
        job_histories_list = json.loads(request.data['job_history_ids']) if 'job_history_ids' in request.data else []
        # Удаляем объекты истории назначения должностей, если у пользователя есть необходимый доступ
        for job_history_id in job_histories_list:
            job_history = open_employee_job_history(job_history_id)
            if not job_history:
                continue
            agency = job_history.agency_employee.agency
            if not check_struct_access_to_page(current_user, agency.headquater, agency, page_codes, "write"):
                return make_error_response("AccessDenied")
            job_history.delete()
        return Response('Successfully deleted', status=status.HTTP_204_NO_CONTENT)

    # Неизвестный метод
    return make_error_response('UnknownError')


""" ************************************* СПИСОК ПРИКРЕПЛЕНИЙ ************************************** """


@login_required
@api_view(['GET'])
def api_org_histories(request):
    """ 
    Возвращает список организаций, к которым прикреплен сотрудник
    """
    current_user = request.user
    agency_pages = ['promo_edit_employee', 'edit_employee', 'broker_edit_employee']
    client_pages = ['hq_edit_employee']

    # Определяем объект сотрудника
    employee = open_employee(request.GET.get('agency_employee_id', None))
    if not employee:
        return make_error_response('Undefined: agency_employee_id')

    # Список прикреплений сотрудника определяется с учетом прав доступа пользователя
    query = None
    # - для менеджера агентства выводится список всех прикреплений сотрудника
    if check_struct_access_to_page(current_user, employee.agency.headquater, employee.agency, agency_pages, 'read'):
        query = OrgHistory.objects.filter(agency_employee=employee)
    # - для менеджера клиента доступны только прикрепления, связанные с его компанией
    else:
        headquarters = []
        clients = employee_clients(employee)
        for client_headquarter in clients:
            if check_struct_access_to_page(current_user, client_headquarter, None, client_pages, 'read'):
                headquarters.append(client_headquarter.id)
        query = OrgHistory.objects.filter(agency_employee=employee, headquater_id__in=headquarters)

    # Возвращаем список прикрпелений
    return Response(OrgHistorySerializer(query, many=True).data)


""" ************************************* СПИСОК СОБЫТИЙ ************************************** """


@login_required
@api_view(['GET'])
def api_employee_events(request):
    """
    Возвращает объединенный список событий, относящихся к сотруднику и состоящий из EmployeeEvent и EmployeeHistory
    """
    current_user = request.user
    agency_pages = ['promo_edit_employee', 'edit_employee', 'broker_edit_employee']
    client_pages = ['hq_edit_employee']

    # Определяем объект сотрудника
    employee = open_employee(request.GET.get('agency_employee_id', None))
    if not employee:
        return make_error_response('Undefined: agency_employee_id')

    # Список событий определяется с учетом прав доступа пользователя
    employee_events = None
    employee_history = None
    # - для менеджера агентства выводится список всех событий
    if check_struct_access_to_page(current_user, employee.agency.headquater, employee.agency, agency_pages, 'read'):
        employee_events = EmployeeEvent.objects.filter(agency_employee=employee)
        employee_history = EmployeeHistory.objects.filter(agency_employee=employee)
    # - для менеджера клиента доступны только события, связанные с его компанией
    else:
        headquarters = []
        clients = employee_clients(employee)
        for client_headquarter in clients:
            if check_struct_access_to_page(current_user, client_headquarter, None, client_pages, 'read'):
                headquarters.append(client_headquarter.id)
        employee_events = EmployeeEvent.objects.filter(agency_employee=employee, headquater_id__in=headquarters)
        employee_history = EmployeeHistory.objects.filter(agency_employee=employee, headquater_id__in=headquarters)

    # Сортируем и объединяем событий в один список
    employee_events = employee_events.order_by('-id')
    employee_history = employee_history.order_by('-id')
    result = EmployeeEventSerializer(employee_events, many=True).data + EmployeeHistorySerializer(employee_history,
                                                                                                  many=True).data
    return Response(sorted(result, key=lambda d: d['dt_created'], reverse=True))


class ApiTransitionAgencyEmployeeView(APIView):

    def post(self, request):
        print('-------ApiTransitionAgancyE------------', request.user,'\n', request.data)
        serializer = TransitionAgencyEmployeeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        open_history = AgencyHistory.objects.filter(agency_employee=serializer.validated_data['agency_employee_id'],
                                                    end__isnull=True).first()
        if open_history and open_history.agency == serializer.validated_data['agency']:
            raise ValueError({'non_field_errors': 'Not edit'})
        # закрываю все
        AgencyHistory.objects.filter(agency_employee=serializer.validated_data['agency_employee_id'],
                                     end__isnull=True).update(
            end=serializer.validated_data['date_transition'] - datetime.timedelta(days=1))
        ah = AgencyHistory(agency=serializer.validated_data['agency'],
                           agency_employee=serializer.validated_data['agency_employee_id'],
                           start=serializer.validated_data['date_transition']).save()
        ag = serializer.validated_data['agency_employee_id']
        ag.agency = serializer.validated_data['agency']
        ag.save()
        try:
            print('Дата транзишон))))',serializer.validated_data['date_transition'])
            org_history = OrgHistory.objects.filter(agency_employee=serializer.validated_data['agency_employee_id']).\
                filter(
                Q(start__lte=serializer.validated_data['date_transition']) and Q( Q(end__isnull=True) or Q(end__gte=serializer.validated_data['date_transition']))
                )
            for i in org_history:
                em_ev = EmployeeEvent(agency=ag.agency,
                                      user=request.user,
                                      agency_employee=serializer.validated_data['agency_employee_id'],
                                      headquater=i.headquater,
                                      organization=i.organization,
                                      ext_number=i.number,
                                      kind="agency")
                em_ev.save()
        except:
            print('Не извлечено добавления события')


        return Response('Created', status=status.HTTP_201_CREATED)
    def get(self, request):
        serializer = GetTransitionAgencyEmployeeSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        eh, start_date = get_last_agency_history_and_startdate(serializer.validated_data['agency_employee_id'])
        # @TODO сейчас все агенства, отсеивать если вложение
        agencys = Agency.objects.filter(headquater=eh.agency.headquater).exclude(
            pk=serializer.validated_data['agency_employee_id'].agency_id)
        return Response(SelectAgencySerializer({'agencies': agencys, 'min_date_transition': start_date}).data)


class ApiAgencyEmployeeHistoryView(APIView):
    def get(self, request):
        serializer = GetTransitionAgencyEmployeeSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        return Response(AgencyHistorySerializer(
            AgencyHistory.objects.filter(agency_employee=serializer.validated_data['agency_employee_id']).order_by(
                '-start'), many=True).data)
