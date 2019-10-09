"""
Copyright 2018 ООО «Верме»

Файл описания сервисов Spyne
Реализует SOAP и REST API
"""
from datetime import timedelta

from django.db.models import Max
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.csrf import csrf_exempt
from spyne.application import Application
from spyne.decorator import rpc
from spyne.model.primitive import Unicode, Date, DateTime, Integer, Boolean
from spyne.server.django import DjangoApplication
from spyne.util.django import DjangoServiceBase
from spyne import error

from apps.employees.methods import *
from apps.notifications.methods import make_notify_data
from apps.outsource.methods import *
from apps.permission.methods import *
from apps.shifts.models import *
from .decorators import *
from .helpers import *
from .models import *

"""
Получение изменений по сменам промоутеров
"""
def _calc_shifts(ctx, dt_change, headquater, agency, amount, party='promo'):
    auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

    # TODO remove
    if not headquater:
        db_headquarter = open_headquarter_by_code('mvideo')
    else:
        # Клиент
        db_headquarter = open_headquarter_by_code(headquater.code)
    if not db_headquarter:
        raise CustomError(f'Headquater {headquater.code} is not registered')

    # Ограничение по агентству (используется для отладки)
    if agency:
        db_agency = open_agency_by_code(agency.code, None)
    else:
        db_agency = None

    # Поиск смен промоутеров, изменных позже dt_change, дополнительно ограничиваем по компании клиента и агентству
    promo_shifts = PromoShift.objects.filter(headquarter=db_headquarter,
                                             dt_change__gt=dt_change, aheadquarter__party=party)
    if db_agency:
        promo_shifts = promo_shifts.filter(agency=db_agency)

    # Если смены найдены, то пытаемся их разбить на группы в соответствии с ограничением на количествво
    if promo_shifts.exists():
        amount = 500
        if not amount or amount < 0:
            amount = 100
        # Т.к. время изменения смены не является уникальным, то определяем максимальное время изменения смены в выборке
        # из заданного числа элементов и возвращаем те смены, которые были изменены до этого времени включительно
        max_change_dtime = promo_shifts.order_by('dt_change')[:amount].aggregate(timestamp=Max('dt_change'))[
            'timestamp']
        promo_shifts = promo_shifts.filter(dt_change__lte=max_change_dtime).select_related('agency_employee')
        promo_count = promo_shifts.count()
        if promo_count > amount + 250:
            try:
                start_sh = int(open(f'/tmp/promo_{dt_change}', 'r').read())
            except FileNotFoundError:
                start_sh = 0
            if start_sh + amount + 250 < promo_count:
                f = open(f'/tmp/promo_{dt_change}', 'w')
                f.write(str(start_sh + amount + 250))
                f.close()
                max_change_dtime = dt_change

            promo_shifts = promo_shifts[start_sh:start_sh + amount + 250]

        # Получение ТН сотрудника в организации на основе OrgHistory
        for shift in promo_shifts:
            if shift.agency_employee:
                shift.agency_employee.oh_number = shift.get_employee_number_in_organization()

        # Возвращаем список смен
        response = dict()
        response['result'] = len(promo_shifts)
        response['timestamp'] = max_change_dtime
        response['shifts_list'] = promo_shifts

    # Нет ни одной смены, возвращаем пустой массив
    else:
        response = dict()
        response['result'] = 0
        response['timestamp'] = dt_change
        response['shifts_list'] = []

    return response


class WFMPortalService(DjangoServiceBase):
    """WEB API"""

    __in_header__ = AuthDataHeader

    """
    Создание заявки на аутсорсинг персонала
    """
    @rpc(
        Unicode(sub_name='guid', min_occurs=1, nillable=False),
        HeadquaterSoapModel.customize(min_occurs=0, nillable=False),
        Date(sub_name='start'), Date(sub_name='end'),
        OrganizationSoapModel,
        AgencySoapModel,
        Unicode(sub_name='state', min_occurs=1, nillable=False),
        Array(ShiftSoapModel),
        Unicode(sub_name='comments', min_occurs=0, nillable=False),
        Unicode(sub_name='user_name', min_occurs=0, nillable=False),
        Unicode(sub_name='email', min_occurs=0, nillable=False),
        _returns=Unicode,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def setOutsourcingRequest(ctx, guid, headquater, start, end, organization, agency, state, shifts, comments,
                              user_name, email):

        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # TODO remove
        if not headquater:
            db_headquarter = open_headquarter_by_code('mvideo')

        # Магазин, сформировавший запрос
        if headquater:
            db_headquarter = open_headquarter_by_code(headquater.code)
            db_organization = open_organization_by_code(organization.code, db_headquarter)
        else:
            db_organization = open_organization_by_code(organization.code, None)
            db_headquarter = db_organization.headquater
        if not db_headquarter:
            raise CustomError(f'REQUEST {guid}: no headquater with code {headquater.code}')
        if not db_organization:
            raise CustomError(f'REQUEST {guid}: no organiztion with code {organization.code}')

        # Агентство, в котором запрашиваем аутсорсинг
        db_agency = open_agency_by_code(agency.code, None)
        if not db_agency:
            raise CustomError(f'REQUEST {guid}: no agency with code {agency.code}')

        # Принимаем запросы только в состоянии launched, повторно запросы и запросы без смен не обрабатываем
        if state != 'launched':
            raise CustomError(f'REQUEST {guid}: state {state} is differ then launched')
        out_req = OutsourcingRequest.objects.filter(guid=guid).first()
        if out_req or not shifts:
            return {'result': 'ok'}

        # Создаем объект запроса
        if not comments:
            comments = ''
        if not user_name:
            user_name = ''
        if not email:
            email = ''
        out_req = OutsourcingRequest.objects.create(guid=guid, headquater=db_headquarter, organization=db_organization,
                                                    agency=db_agency, state='accepted', start=start, end=end,
                                                    comments=comments, user_name=user_name, email=email)
        # Создаем связанные с запросом смены
        for s in shifts:
            try:
                job = Job.objects.get(code=s.job.code)
            except Job.DoesNotExist:
                raise CustomError(f'REQUEST {guid}, SHIFT {s.guid}: no job with code {s.job.code}')
            if s.start > s.end:
                raise CustomError(f'REQUEST {guid}, SHIFT {s.guid}: start > end')
            if s.worktime < 0:
                raise CustomError(f'REQUEST {guid}, SHIFT {s.guid}: worktime = {s.worktime} < 0')
            OutsourcingShift.objects.create(guid=s.guid, headquater=db_headquarter, state=s.state,
                                            start=s.start, end=s.end, worktime=s.worktime, job=job,
                                            request=out_req, agency=db_agency, start_date=s.start)

        # Создаем и отправляем уведомления о новой заявке
        make_notify_data(out_req, 'agency', 'wait_req_template')
        return {'result': 'ok'}

    """
        Получение данных по запросам, чей статус был обновлен раньше определенного времени
    """
    @rpc(
        DateTime(sub_name='timestamp', min_occurs=1, nillable=False),
        HeadquaterSoapModel.customize(min_occurs=0, nillable=False),
        Integer(sub_name='amount', min_occurs=0, nillable=False),
        _returns=ComplexRequestsResponseSoapModel,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def getOutsourcingRequests(ctx, dt_change, headquater, amount):
        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # TODO remove
        if not headquater:
            db_headquarter = open_headquarter_by_code('mvideo')
        else:
            # Клиент
            db_headquarter = open_headquarter_by_code(headquater.code)
        if not db_headquarter:
            raise CustomError(f'Headquater {headquater.code} is not registered')

        response = dict()
        response['requests_list'] = []

        # Ограничинваем максимальное количество запросов, возвращаемых за 1 раз
        if not amount or amount < 0:
            amount = 100

        # Поиск смен
        out_requests = OutsourcingRequest.objects.filter(headquater=db_headquarter,
                                                         dt_ready__gt=dt_change,
                                                         state='ready')
        out_requests = out_requests.order_by('dt_ready')[:amount]

        # Формируем результат
        if not out_requests:
            response['result'] = len(out_requests)
            response['timestamp'] = dt_change
        else:
            response['result'] = len(out_requests)
            response['timestamp'] = out_requests.aggregate(timestamp=Max('dt_ready'))['timestamp']
            response['requests_list'] = out_requests

        return response

    """
    Получение данных по запросу и связанным с ним сменам
    """
    @rpc(
        Unicode(sub_name='guid', min_occurs=1, nillable=False),
        HeadquaterSoapModel.customize(min_occurs=0, nillable=False),
        _returns=ComplexOutsourcingRequestSoapModel,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def getOutsourcingRequest(ctx, guid, headquater):
        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # TODO remove
        if not headquater:
            db_headquarter = open_headquarter_by_code('mvideo')
        else:
            # Клиент
            db_headquarter = open_headquarter_by_code(headquater.code)
        if not db_headquarter:
            raise CustomError(f'Headquater {headquater.code} is not registered')

        try:
            out_request = OutsourcingRequest.objects.get(guid=guid,
                                                         headquater=db_headquarter)
            shifts = OutsourcingShift.objects.filter(request=out_request,
                                                     headquater=db_headquarter).select_related('job')
            out_request.shifts = shifts
            return out_request
        except:
            raise CustomError(f'REQUEST {guid}: no OutsourcingRequest is found')

    """
    Получение изменений по сменам на аутсорсинг
    """
    @rpc(
        DateTime(sub_name='timestamp', min_occurs=1, nillable=False),
        HeadquaterSoapModel.customize(min_occurs=0, nillable=False),
        Integer(sub_name='amount', min_occurs=0, nillable=False),
        _returns=ComplexShiftsResponseSoapModel,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def getOutsourcingShifts(ctx, dt_change, headquater, amount):
        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # TODO remove
        if not headquater:
            db_headquarter = open_headquarter_by_code('mvideo')
        else:
            # Клиент
            db_headquarter = open_headquarter_by_code(headquater.code)
        if not db_headquarter:
            raise CustomError(f'Headquater {headquater.code} is not registered')

        response = dict()
        response['shifts_list'] = []

        # Ограничинваем максимальное количество смен, возвращаемых за 1 раз
        if not amount or amount < 0:
            amount = 100

        # Поиск смен
        out_shifts = OutsourcingShift.objects.filter(headquater=db_headquarter,
                                                     dt_change__gt=dt_change, state='accept')
        out_shifts = out_shifts.order_by('dt_change').select_related('agency_employee')[:amount]

        # Получение ТН сотрудника в организации на основе OrgHistory
        for shift in out_shifts:
            if shift.agency_employee:
                shift.agency_employee.oh_number = shift.get_employee_number_in_organization()
        # Формируем результат
        if not out_shifts:
            response['result'] = len(out_shifts)
            response['timestamp'] = dt_change
        else:
            response['result'] = len(out_shifts)
            response['timestamp'] = out_shifts.aggregate(timestamp=Max('dt_change'))['timestamp']
            response['shifts_list'] = out_shifts

        return response

    """
    Получение смен промоутеров
    """    
    @rpc(
        DateTime(sub_name='timestamp', min_occurs=1, nillable=False),
        HeadquaterSoapModel.customize(min_occurs=0, nillable=False),
        AgencySoapModel.customize(min_occurs=0, nillable=False),
        Integer(sub_name='amount', min_occurs=0, nillable=False),
        _returns=ComplexPromoShiftsResponseSoapModel,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def getPromoShifts(ctx, dt_change, headquater, agency, amount):
        return _calc_shifts(ctx, dt_change, headquater, agency, amount, party='promo')

    """
    Получение смен брокеров
    """    
    @rpc(
        DateTime(sub_name='timestamp', min_occurs=1, nillable=False),
        HeadquaterSoapModel.customize(min_occurs=0, nillable=False),
        AgencySoapModel.customize(min_occurs=0, nillable=False),
        Integer(sub_name='amount', min_occurs=0, nillable=False),
        _returns=ComplexPromoShiftsResponseSoapModel,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def getBrokerShifts(ctx, dt_change, headquater, agency, amount):
        return _calc_shifts(ctx, dt_change, headquater, agency, amount, party='broker')

    """
    Удаление смены из заявки на аутсорсинг по решению управляюего магазином
    """
    @rpc(
        Array(ShiftDeleteSoapModel),
        HeadquaterSoapModel.customize(min_occurs=0, nillable=False),
        _returns=Unicode,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def deleteOutsourcingShifts(ctx, shifts, headquater):
        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # TODO remove
        if not headquater:
            db_headquarter = open_headquarter_by_code('mvideo')
        else:
            # Клиент
            db_headquarter = open_headquarter_by_code(headquater.code)
        if not db_headquarter:
            raise CustomError(f'Headquater {headquater.code} is not registered')

        # Выходим, если массив смен не задан
        if not shifts:
            return {'result': 'ok'}

        # Помечаем смены как удаленные и формируем уведомления
        for shift in shifts:
            # ----------------------------------------------------------
            out_shift = OutsourcingShift.objects.filter(guid=shift.guid, headquater=db_headquarter).first()
            if not out_shift:
                continue
            # Создаем и отправляем уведомления об удаленной смене
            make_notify_data(out_shift, 'agency', 'delete_shift_template')

            # Меняем состояние на удалена
            out_shift.state = 'delete'
            out_shift.save(update_fields=['state'])
            # -----------------------------------------------------------
        return {'result': 'ok'}

    """
    Получение изменений в данных сотрудников
    """
    @rpc(
        DateTime(sub_name='timestamp', min_occurs=1, nillable=False),
        HeadquaterSoapModel.customize(min_occurs=0, nillable=False),
        Integer(sub_name='amount', min_occurs=1, nillable=False),
        _returns=ComplexEmployeeEventResponseSoapModel,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def getEmployeeEvents(ctx, timestamp, headquater, amount):
        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # Ограничинваем максимальное количество событий, возвращаемых за 1 раз
        if amount <= 0:
            amount = 100

        # TODO remove
        if not headquater:
            db_headquarter = open_headquarter_by_code('mvideo')
        else:
            # Клиент
            db_headquarter = open_headquarter_by_code(headquater.code)
        if not db_headquarter:
            raise CustomError(f'Headquater {headquater.code} is not registered')

        # Поиск событий, начиная с заданного в запросе timestamp
        response = dict()
        response['events_list'] = []
        events = EmployeeEvent.objects.filter(dt_created__gt=timestamp, headquater=db_headquarter). \
                     select_related('agency_employee', 'agency').order_by('id')[:amount]
        # Обогощаем найденные события доп. полями
        for event in events:
            # Тип агентства
            event.agency.party = event.agency.headquater.party
            # Документы сотрудника
            event.agency_employee.documents = EmployeeDoc.objects.filter(
                agency_employee=event.agency_employee).order_by('-id')
            # Обнуляем лишние поля
            if event.kind != 'recruitment':
                event.recruitment_date = None
            if event.kind != 'dismissal':
                event.dismissal_reason = None
                event.dismissal_date = None
                event.blacklist = None
        # Добавляем возвращемые события в ответное сообщение
        response['result'] = len(events)
        if events:
            response['timestamp'] = events.aggregate(timestamp=Max('dt_created'))['timestamp']
            response['events_list'] = events
        return response

    """DEPRICATED"""
    @rpc(
        HeadquaterSoapModel.customize(min_occurs=1, nillable=False),
        OrganizationSoapModel.customize(min_occurs=1, nillable=False),
        AgencySoapModel.customize(min_occurs=1, nillable=False),
        EmployeeMinSoapModel,
        EventSoapModel.customize(sub_name='event'),
        Unicode(sub_name='kind', min_occurs=1, nillable=False),
        Unicode(sub_name='number', min_occurs=0, nillable=False),
        Date(sub_name='recruitment_date', min_occurs=0, nillable=False),
        Date(sub_name='recruitment_state', min_occurs=0, nillable=False),
        Date(sub_name='dismissal_date', min_occurs=0, nillable=False),
        Unicode(sub_name='reject_reason', min_occurs=0, nillable=False),
        Unicode(sub_name='dismissal_reason', min_occurs=0, nillable=False),
        _returns=Unicode,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def setEventHistory(
            ctx, headquater, organization, agency, employee, employeeevent, kind,
            number, recruitment_date, recruitment_state, dismissal_date, reject_reason, dismissal_reason
    ):
        raise CustomError('Method is deprocated')
        
        # TODO изменить проверку доступа с is_superuser

        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        headquater_id = get_headquater_id(headquater.code)

        org = Organization.objects.get(code=organization.code, headquater_id=headquater_id)
        if not org:
            raise CustomError('No organiztion')

        agn = Agency.objects.get(code=agency.code)
        if not agn:
            raise CustomError('No agency')

        emp = AgencyEmployee.objects.get(number=employee.number, agency=agn)
        if not emp:
            raise CustomError('No employee')

        event = EmployeeEvent.objects.get(guid=employeeevent.guid)

        user = User.objects.get(username=ctx.in_header.login)

        if kind not in dict(EVENT_HISTORY_KIND_CHOICES):
            raise CustomError('No kind')
        elif kind == 'accept_recruitment':

            if not recruitment_date:
                raise CustomError('No recruitment_date')

            if recruitment_state not in ['active', 'inactive']:
                raise CustomError('No recruitment_state')

            """Создаем объект внешнего события"""
            EmployeeHistory.objects.create(user=user, headquater_id=headquater_id, organization=org,
                                           event=event, agency_employee=emp, agency=agn, kind=kind,
                                           recruitment_date=recruitment_date,
                                           recruitment_state=recruitment_state)

            if recruitment_state == 'active':
                """Создаем объект назначения"""
                OrgHistory.objects.create(headquater_id=headquater_id, organization=org, agency_employee=emp,
                                          number=number, start=recruitment_date)

            """Устанавливаем EmployeeEvent флаг, что ответ на него получен"""
            event.answer_received = True
            event.save(update_fields=['answer_received'])
        elif kind == 'reject_recruitment':

            if not reject_reason:
                raise CustomError('No reject_reason')

            """Создаем объект внешнего события"""
            EmployeeHistory.objects.create(user=user, headquater_id=headquater_id, organization=org,
                                           event=event, agency_employee=emp, agency=agn, kind=kind,
                                           reject_reason=reject_reason)
            """Устанавливаем EmployeeEvent флаг, что ответ на него получен"""
            event.answer_received = True
            event.save(update_fields=['answer_received'])

        elif kind == 'dismissal':

            if not dismissal_date or not dismissal_reason:
                raise CustomError('No dismissal date or reason')

            """Ищем назначение и устанавливаем дату увольнения"""
            org_history = OrgHistory.objects.get(organization=org, agency_employee=emp)
            if not org_history:
                raise CustomError('No OrgHistory')
            org_history.end = dismissal_date - timedelta(days=1)
            org_history.save(update_fields=['end'])

            """Ищем смены данного сотрудника после даты увольнения и снимаем назначение"""
            OutsourcingShift.objects.filter(agency_employee=emp,
                                            start_date__gt=dismissal_date - timedelta(days=1),
                                            headquater_id=headquater_id).update(agency_employee=None)

            """Создаем объект внешнего события"""
            EmployeeHistory.objects.create(user=user, headquater_id=headquater_id, organization=org,
                                           event=event, agency_employee=emp, agency=agn, kind=kind,
                                           dismissal_date=dismissal_date, dismissal_reason=dismissal_reason)
            """Устанавливаем EmployeeEvent флаг, что ответ на него получен"""
            event.answer_received = True
            event.save(update_fields=['answer_received'])

            """Устанавливаем сотруднику дату обновления данных по API"""
            event.agency_employee.last_external_update = timezone.now()
            event.agency_employee.save(update_fields=['last_external_update'])

        return "ok"

    """Подтверждение или отказ в приеме сотрудника из кадровой системы клиента"""
    @rpc(
        EventSoapModel2.customize(sub_name='event', min_occurs=1, nillable=False),
        Unicode(sub_name='status', min_occurs=1, nillable=False),
        Unicode(sub_name='recruitmentState', min_occurs=0, nillable=False, default='active'),
        Date(sub_name='recruitmentDate', min_occurs=0, nillable=False),
        Unicode(sub_name='externalNumber', min_occurs=0, nillable=False),
        Unicode(sub_name='rejectReason', min_occurs=0, nillable=False),
        _returns=Unicode,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def setRecruitmentStatus(ctx, employeeevent, status, recruitmentState, recruitmentDate, externalNumber,
                             rejectReason):
        user = User.objects.get(username=ctx.in_header.login)
        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # Проверка параметров
        event = EmployeeEvent.objects.get(guid=employeeevent.guid)
        if not event:
            raise CustomError(f'Event {employeeevent.guid} is undefined')
        if recruitmentState and recruitmentState not in ['active', 'inactive']:
            raise CustomError('No recruitmentState')
        if status not in ['accept', 'reject']:
            return

        # Подтверждение регистрации
        if status == 'accept':
            error = accept_employee_attach(user, event, recruitmentState, recruitmentDate, externalNumber)
        # Регистрация отклонена
        else:
            error = reject_employee_attach(user, event, rejectReason)
        # Обработчик ошибок
        if error:
            raise CustomError(error)

        # Устанавливаем сотруднику дату обновления данных по API
        event.agency_employee.last_external_update = timezone.now()
        event.agency_employee.save(update_fields=['last_external_update'])

        return

    """Открепление сотрудника от клиента по запросу из кадровой системы"""
    @rpc(
        HeadquaterSoapModel.customize(min_occurs=1, nillable=False),
        OrganizationSoapModel,
        AgencySoapModel.customize(min_occurs=1, nillable=False),
        Unicode(sub_name='externalNumber', min_occurs=1, nillable=False),
        Date(sub_name='dismissalDate', min_occurs=1, nillable=False),
        Unicode(sub_name='dismissalReason', min_occurs=1, nillable=False),
        Boolean(sub_name='blacklist', min_occurs=1, nillable=False),
        _returns=Unicode,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def dismissEmployee(ctx, headquater, organization, agency, ext_number, dismissal_date, dismissal_reason, blacklist):
        user = User.objects.get(username=ctx.in_header.login)
        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # Проверка параметров
        db_headquarter = open_headquarter_by_code(headquater.code)
        if not db_headquarter:
            raise CustomError(f'Headquater {headquater.code} is not found')
        if organization:
            db_organization = open_organization_by_code(organization.code, db_headquarter)
            if not db_organization:
                raise CustomError(f'Organization {organization.code} is not found')
        else:
            db_organization = None
        db_agency = open_agency_by_code(agency.code, None)
        if not db_agency:
            raise CustomError(f'Agency {agency.code} is not found')

        # Определяем увольняемого сотрудника
        employees = employees_by_ext_number(db_headquarter, db_agency, ext_number)
        for employee in employees:
            dismiss_employee(user, employee, dismissal_date, dismissal_reason, blacklist, db_headquarter,
                             db_organization)
            # Устанавливаем сотруднику дату обновления данных по API
            employee.last_external_update = timezone.now()
            employee.save(update_fields=['last_external_update'])
        return

    ########
    @rpc(
        HeadquaterSoapModel.customize(min_occurs=1, nillable=False),
        Array(OrgunitSoapModel.customize(min_occurs=1, nillable=False)),
        Array(OrglinkSoapModel.customize(min_occurs=0, nillable=False)),
        _returns=Unicode,
        _throws=[AuthenticationError, AuthorizationError, CustomError]
    )
    @soap_logger
    @check_auth_data
    def setOrgunits(
            ctx, headquater, orgunits, orglinks
    ):
        """Set Orgunits. Синхронизитрует орг. структуру на основе данных из портала планирования"""

        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # Headquarter
        headquater_id = get_headquater_id(headquater.code)

        # Organizations
        orgunits_received = 0
        orgunits_created = 0
        orgunits_errors = 0
        if orgunits:
            for orgunit in orgunits:
                orgunits_received += 1
                org, org_created = Organization.objects.get_or_create(code=orgunit.code, headquater_id=headquater_id)
                if org_created:
                    orgunits_created += 1
                org.name = orgunit.name
                org.address = orgunit.address
                org.kind = 'store'
                if orgunit.parent and org_created:
                    parent_org = Organization.objects.filter(code=orgunit.parent.code,
                                                             headquater_id=headquater_id).first()
                    if parent_org:
                        org.parent = parent_org
                    else:
                        default, default_created = Organization.objects.get_or_create(
                            code=headquater.code + '_city_undefined',
                            name='Город не определен',
                            headquater_id=headquater_id, kind='city')
                        org.parent = default
                org.last_external_update = timezone.now()
                org.save()

        # OrgLinks
        orglinks_received = 0
        orglinks_created = 0
        orglinks_errors = 0
        if orglinks:
            for orglink_imp in orglinks:
                orglinks_received += 1
                organization = Organization.objects.filter(code=orglink_imp.organization.code).first()
                if not organization:
                    orglinks_errors += 1
                    continue
                agency = Agency.objects.filter(code=orglink_imp.agency.code).first()
                if not agency:
                    orglinks_errors += 1
                    continue
                _, orglink_created = OrgLink.objects.get_or_create(agency=agency, organization=organization,
                                                                   headquater_id=headquater_id)
                if orglink_created:
                    orglinks_created += 1

        return {
            'result': 'ok',
            'orgunits_received': orgunits_received,
            'orgunits_created': orgunits_created,
            'orgunits_errors': orgunits_errors,
            'orglinks_received': orglinks_received,
            'orglinks_created': orglinks_created,
            'orglinks_errors': orglinks_errors,
        }

    @rpc(
        HeadquarterSoapModel.customize(min_occurs=1, nillable=False),
        UserExtSoapModel.customize(sub_name='user', min_occurs=1, nillable=False),
        Array(AccessProfileSoapModel, sub_name='accessProfiles').customize(min_occurs=1, nillable=False),
        _throws=[AuthenticationError, AuthorizationError, error.ResourceNotFoundError]
    )
    @soap_logger
    @check_auth_data
    def setUser(ctx, headquarter, user, access_list):
        auth_and_check_perms(ctx.in_header.login, ctx.in_header.password)

        # Обновляем или создаем сотрудника
        user_defaults = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'is_active': user.is_active
        }
        db_user, created = User.objects.update_or_create(username=user.username, defaults=user_defaults)
        db_headquarter = open_headquarter_by_code(headquarter.code)
        db_access_role = None

        # Установка прав доступа
        if access_list is None:
            access_list = []

        for access_profile in access_list:
            try:
                db_organization = open_organization_by_code(access_profile.unit.code, db_headquarter)
            except error.ResourceNotFoundError:
                continue

            if access_profile.role is not None:
                db_access_role = open_role_by_code(access_profile.role.code)

            if db_access_role is None:
                raise error.ResourceNotFoundError('accessRole')

            profile, _ = AccessProfile.objects.update_or_create(
                user=db_user,
                unit_type=ContentType.objects.get_for_model(db_organization),
                unit_id=db_organization.id,
                role=db_access_role,
                headquater=db_headquarter)


soap_app = Application(
    [WFMPortalService],
    'http://outsourcing.verme.ru/api/soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

rest_app = Application(
    [WFMPortalService],
    'http://outsourcing.verme.ru/api/soap',
    in_protocol=JsonDocument(validator='soft'),
    out_protocol=JsonDocument()
)

outsourcing_soap_service = csrf_exempt(DjangoApplication(soap_app))
outsourcing_rest_service = csrf_exempt(DjangoApplication(rest_app))
