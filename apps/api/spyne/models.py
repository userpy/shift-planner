#
# Copyright 2018 ООО «Верме»
#
# Файл моделей Spyne
#

from spyne.model import primitive, complex
from spyne.model.complex import ComplexModel, Array
from spyne.util.odict import odict


NAMESPACE = "http://outsourcing.verme.ru/api/soap"


od = odict()
od['login'] = primitive.Mandatory.String
od['password'] = primitive.Mandatory.String

AuthDataHeader = ComplexModel.produce(NAMESPACE, 'authData', od)

od = odict()
od['code'] = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)
AgencySoapModel = ComplexModel.produce(NAMESPACE, 'agency', od)

od = odict()
od['code'] = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)
od['party'] = primitive.Unicode(sub_name='party', min_occurs=1, nillable=False)
AgencyEventSoapModel = ComplexModel.produce(NAMESPACE, 'agency_event', od)

od = odict()
od['code'] = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)
OrganizationSoapModel = ComplexModel.produce(NAMESPACE, 'organization', od)

od = odict()
od['code'] = primitive.Unicode(sub_name='code')
JobSoapModel = ComplexModel.produce(NAMESPACE, 'job', od)

od = odict()
od['agency'] = primitive.Unicode(sub_name='agency__code')
od['job'] = primitive.Unicode(sub_name='job__code')
od['start_date'] = primitive.Date(sub_name='start_date')
od['end_date'] = primitive.Date(sub_name='end_date')
AgencyHistorySoapModel = ComplexModel.produce(NAMESPACE, 'agency_history', od)

"""Модель для импорта орг.единиц из портала планирования"""
od = odict()
od['name'] = primitive.Unicode(sub_name='name', min_occurs=1, nillable=False)
od['code'] = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)
od['address'] = primitive.Unicode(sub_name='address', min_occurs=1, nillable=False)
od['parent'] = OrganizationSoapModel.customize(sub_name='parent', min_occurs=0, nillable=True)
od['agency_history'] = Array(AgencyHistorySoapModel)
OrgunitSoapModel = ComplexModel.produce(NAMESPACE, 'orgunit', od)

"""Модель для импорта функций из портала планирования"""
od = odict()
od['code'] = primitive.Unicode(sub_name='code')
od['name'] = primitive.Unicode(sub_name='name')
od['jobs'] = Array(JobSoapModel.customize(min_occurs=0, nillable=False))
JobSoapModelImport = ComplexModel.produce(NAMESPACE, 'job_import', od)

"""Модель для импорта агентств из портала планирования"""
od = odict()
od['code'] = primitive.Unicode(sub_name='code')
od['name'] = primitive.Unicode(sub_name='name')
od['jobs'] = Array(primitive.Unicode)
AgencySoapModelImport = ComplexModel.produce(NAMESPACE, 'agency_import', od)

"""Модель для импорта связей агенство-организация из портала планирования"""
od = odict()
od['agency'] = AgencySoapModel.customize(sub_name='agency', min_occurs=1, nillable=False)
od['organization'] = OrganizationSoapModel.customize(sub_name='organization', min_occurs=1, nillable=False)
OrglinkSoapModel = ComplexModel.produce(NAMESPACE, 'orglink', od)

od = odict()
od['guid'] = primitive.Uuid(sub_name='guid')
od['state'] = primitive.Unicode(sub_name='state')
od['start'] = primitive.DateTime(sub_name='start')
od['end'] = primitive.DateTime(sub_name='end')
od['worktime'] = primitive.Integer(sub_name='worktime')
od['job'] = JobSoapModel

ShiftSoapModel = ComplexModel.produce(NAMESPACE, 'shift', od)

od = odict()
od['guid'] = primitive.Uuid(sub_name='guid')
ShiftDeleteSoapModel = ComplexModel.produce(NAMESPACE, 'shift', od)

od = odict()
od['name'] = primitive.Unicode(sub_name='full_name')
od['number'] = primitive.Unicode(sub_name='agencyNumber')
od['oh_number'] = primitive.Unicode(sub_name='number')
od['date_of_birth'] = primitive.Date(sub_name='dateOfBirth')
EmployeeSoapModel = ComplexModel.produce(NAMESPACE, 'employee', od)

od = odict()
od['code'] = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)
HeadquaterSoapModel = ComplexModel.produce(NAMESPACE, 'headquater', od)

od = odict()
od['code'] = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)
HeadquarterSoapModel = ComplexModel.produce(NAMESPACE, 'headquarter', od)

od = odict()
od['code'] = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)
od['name'] = primitive.Unicode(sub_name='name', min_occurs=1, nillable=False)
od['color'] = primitive.Unicode(sub_name='color', min_occurs=0, nillable=True)
StoreAreaSoapModel = ComplexModel.produce(NAMESPACE, 'store_area', od)

od = odict()
od['username'] = primitive.Unicode(sub_name='username')
UserSoapModel = ComplexModel.produce(NAMESPACE, 'user', od)

od = odict()
od['guid'] = primitive.Uuid(sub_name='guid')
EventSoapModel = ComplexModel.produce(NAMESPACE, 'event_min', od)

od = odict()
od['guid'] = primitive.Uuid(sub_name='guid', min_occurs=1, nillable=False)
EventSoapModel2 = ComplexModel.produce(NAMESPACE, 'event_min_req', od)

od = odict()
od['code'] = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)
DocumentTypeSoapModel = ComplexModel.produce(NAMESPACE, 'docType', od)

od = odict()
od['guid'] = primitive.Uuid(sub_name='guid', min_occurs=1, nillable=False)
od['start'] = primitive.Date(sub_name='start', min_occurs=1, nillable=False)
od['end'] = primitive.Date(sub_name='end', min_occurs=0, nillable=True)
od['comments'] = primitive.Unicode(sub_name='comments')
od['doc_type'] = DocumentTypeSoapModel.customize(sub_name='docType')
DocumentSoapModel = ComplexModel.produce(NAMESPACE, 'document', od)


class EmployeeExtSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "employee_ext"

    number = primitive.Unicode(sub_name='number')
    firstname = primitive.Unicode(sub_name='firstname')
    surname = primitive.Unicode(sub_name='surname')
    patronymic = primitive.Unicode(sub_name='patronymic')
    gender = primitive.Unicode(sub_name='gender')
    date_of_birth = primitive.Date(sub_name='dateOfBirth')
    place_of_birth = primitive.Unicode(sub_name='placeOfBirth')
    receipt = primitive.Date(sub_name='receipt')
    dismissal = primitive.Date(sub_name='dismissal')
    documents = Array(DocumentSoapModel, sub_name='documents')

    class Attributes(ComplexModel.Attributes):
        declare_order = 'declared'


od = odict()
od['number'] = primitive.Unicode(sub_name='number')
EmployeeMinSoapModel = ComplexModel.produce(NAMESPACE, 'employee_min', od)


class EmployeeEventSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "event"

    guid = primitive.Uuid(sub_name='guid')
    dt_created = primitive.DateTime(sub_name='created')
    headquater = HeadquaterSoapModel
    organization = OrganizationSoapModel
    agency = AgencyEventSoapModel.customize(sub_name='agency')
    agency_employee = EmployeeExtSoapModel.customize(sub_name='employee')
    ext_number = primitive.Unicode(sub_name='externalNumber')
    user = UserSoapModel
    kind = primitive.Unicode(sub_name='kind')
    recruitment_date = primitive.Date(sub_name='recruitmentDate')
    dismissal_date = primitive.Date(sub_name='dismissalDate')
    dismissal_reason = primitive.Unicode(sub_name='dismissalReason')
    answer_received = primitive.Boolean(sub_name='answerReceived')
    blacklist = primitive.Boolean(sub_name='blacklist')

    class Attributes(ComplexModel.Attributes):
        declare_order = 'declared'


od = odict()
od['guid'] = primitive.Uuid(sub_name='guid')
od['state'] = primitive.Unicode(sub_name='state')
od['start'] = primitive.DateTime(sub_name='start')
od['end'] = primitive.DateTime(sub_name='end')
od['worktime'] = primitive.Integer(sub_name='worktime')
od['agency_employee'] = EmployeeSoapModel

ShiftExtendedSoapModel = ComplexModel.produce(NAMESPACE, 'shift', od)


od = odict()
od['guid'] = primitive.Uuid(sub_name='guid')
od['state'] = primitive.Unicode(sub_name='state')
od['start_date'] = primitive.Date(sub_name='start_date')
od['start'] = primitive.DateTime(sub_name='start')
od['end'] = primitive.DateTime(sub_name='end')
od['worktime'] = primitive.Integer(sub_name='worktime')
od['duration'] = primitive.Integer(sub_name='duration')
od['aheadquarter'] = HeadquaterSoapModel.customize(sub_name='aheadquarter')
od['agency'] = AgencySoapModel.customize(sub_name='agency')
od['organization'] = OrganizationSoapModel.customize(sub_name='organization')
od['store_area'] = StoreAreaSoapModel.customize(sub_name='store_area')
od['agency_employee'] = EmployeeSoapModel

PromoShiftExtendedSoapModel = ComplexModel.produce(NAMESPACE, 'promo_shift', od)


class SimpleOutsourcingRequestSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = 'requestSimple'

    guid = primitive.Uuid(sub_name='guid')


class ComplexRequestsResponseSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "requestsresponseComplex"

    result = primitive.Integer(sub_name='result')
    timestamp = primitive.DateTime(sub_name='timestamp')
    requests_list = Array(SimpleOutsourcingRequestSoapModel, sub_name='requests')


class ComplexOutsourcingRequestSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = 'outsourcingComplex'

    guid = primitive.Uuid(sub_name='guid')
    start = primitive.Date(sub_name='start')
    end = primitive.Date(sub_name='end')
    organization = OrganizationSoapModel
    agency = AgencySoapModel
    state = primitive.Unicode(sub_name='state')
    shifts = Array(ShiftSoapModel, sub_name='shifts')


class ComplexPromoShiftsResponseSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "promoshiftsresponseComplex"

    result = primitive.Integer(sub_name='result')
    timestamp = primitive.DateTime(sub_name='timestamp')
    shifts_list = Array(PromoShiftExtendedSoapModel, sub_name='shifts')


class ComplexShiftsResponseSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "shiftsresponseComplex"

    result = primitive.Integer(sub_name='result')
    timestamp = primitive.DateTime(sub_name='timestamp')
    shifts_list = Array(ShiftExtendedSoapModel, sub_name='shifts')


class ComplexEmployeeEventResponseSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "eventresponseComplex"

    result = primitive.Integer(sub_name='result')
    timestamp = primitive.DateTime(sub_name='timestamp')
    events_list = Array(EmployeeEventSoapModel, sub_name='events')

    class Attributes(ComplexModel.Attributes):
        declare_order = 'declared'


class UserExtSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "user_ext"

    username = primitive.Unicode(sub_name='username', min_occurs=1, nillable=False)
    email = primitive.Unicode(sub_name='email', min_occurs=1, nillable=False)
    first_name = primitive.Unicode(sub_name='firstName', min_occurs=1, nillable=False)
    last_name = primitive.Unicode(sub_name='lastName', min_occurs=1, nillable=False)
    is_active = primitive.Boolean(sub_name='isActive', min_occurs=1, nillable=False)

    class Attributes(ComplexModel.Attributes):
        declare_order = 'declared'


class SimpleAccessRoleSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "simpleAccessRole"

    code = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)


class SimpleOrgunitSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "simpleOrgunit"

    code = primitive.Unicode(sub_name='code', min_occurs=1, nillable=False)


class AccessProfileSoapModel(ComplexModel):
    __namespace__ = NAMESPACE
    __type_name__ = "accessProfile"

    unit = SimpleOrgunitSoapModel.customize(sub_name='unit', min_occurs=1, nillable=False)
    role = SimpleAccessRoleSoapModel.customize(sub_name='accessRole')
    start_date = primitive.Date(sub_name='start')
    end_date = primitive.Date(sub_name='end')

    class Attributes(ComplexModel.Attributes):
        declare_order = 'declared'
