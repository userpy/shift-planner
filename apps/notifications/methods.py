from .models import *
from apps.claims.models import ClaimRequest, ClaimMessage
from apps.shifts.models import OutsourcingRequest, OutsourcingShift
from apps.outsource.models import Config
from apps.permission.methods import get_available_users_by_client, get_available_users_by_agency, get_client_base_org


def make_notify_data(instance, party, template):
    print('0) instance Request_id {}'.format(instance.request))
    # Объект оповещения, сторона для оповещения, шаблон оповещения
    print('0)make notification')
    # Массив данных для уведомлений
    notify_data = dict()

    # Список email
    notify_emails = []

    # Сообщение
    if isinstance(instance, ClaimMessage):
        # Добавляем информацию о претензии
        notify_data.update({"message": make_message_data(instance)})
        # Меняем instance на claim
        instance = instance.claim
    # Претензия
    if isinstance(instance, ClaimRequest):
        # Добавляем информацию о претензии
        notify_data.update({"claim": make_claim_data(instance)})
        # Добавляем email из претензии в список для отправки
        notify_emails.append({'email': instance.email, 'full_name': instance.user_name})

    # Заявка
    if isinstance(instance, OutsourcingRequest):

        # Добавляем информацию о претензии
        notify_data.update({"request": make_request_data(instance)})
        # Добавляем email из заявки в список для отправки
        notify_emails.append({'email': instance.email, 'full_name': instance.user_name})

    # Смена

    if isinstance(instance, OutsourcingShift):
        # Добавляем информацию о претензии
        notify_data.update({"shift": make_shift_data(instance)})

        if instance.agency_employee:

            notify_data.update({"employee": make_employee_data(instance.agency_employee)})

        #Меняем instance на request

        request_id = instance.request_id
        request_data = instance.request

        instance = instance.request

        instance.request_id = request_id
        instance.request = request_data



    # Определяем шаблон для уведомления
    template = Config.objects.filter(headquater=instance.headquater, key=template).first()

    # Если нет шаблона - выходим
    if not template:
        return

    # Проверка стороны
    if party not in ['agency', 'client']:
        return

    if party == 'agency':
        notify_users = User.objects.filter(id__in=get_available_users_by_agency(instance.agency.id),
                                           email__isnull=False)
        notify_emails = []
    else:
        base_org = get_client_base_org(instance.headquater.id)
        if not base_org:
            return
        notify_users = User.objects.filter(id__in=get_available_users_by_client(base_org.id),
                                           email__isnull=False)

    # Если нет пользователей для рассылки уведомления
    if not notify_users:
        return
    # Заполняем основные данные
    notify_data.update({"headquater": make_headquater_data(instance.headquater)})
    notify_data.update({"request": make_request_data(instance.request)})
    notify_data.update({"organization": make_organization_data(instance.organization)})
    notify_data.update({"agency": make_agency_data(instance.agency)})
    notify_data.update({"party": party})

    # Создаем уведомления

    make_notifications(notify_users, notify_emails, template.value, notify_data)


# Данные о заявке
def make_request_data(instance):

    # Вычисление значений для уведомления
    # Количество смен в заявке
    shifts = OutsourcingShift.objects.filter(request=instance)
    accept = shifts.filter(state='accept').count()
    reject = shifts.filter(state='reject').count()
    shifts = shifts.values('job__name')
    # Должности в сменах
    jobs = []
    for shift in shifts:
        if shift['job__name'] not in jobs:
            jobs.append(shift['job__name'])

    data = dict()
    data['id'] = instance.id
    data['guid'] = str(instance.guid)
    data['comments'] = instance.comments
    data['shift_count'] = len(shifts)
    data['shift_jobs'] = ' '.join(jobs)
    data['start_date'] = instance.start.isoformat()
    data['end_date'] = instance.end.isoformat()
    data['accept_total'] = accept
    data['reject_total'] = reject
    return data


# Данные о смене
def make_shift_data(instance):

    data = dict()
    data['guid'] = str(instance.guid)
    data['start_date'] = instance.start_date.isoformat()
    data['job'] = instance.job.name
    data['last_state'] = instance.get_state_display()
    return data


# Данные о сотруднике
def make_employee_data(instance):

    data = dict()
    data['in']
    data['surname'] = instance.surname
    data['first_name'] = instance.firstname
    data['patronymic'] = instance.patronymic
    data['number'] = instance.number
    return data


# Данные об агентстве
def make_agency_data(instance):

    data = dict()
    data['code'] = instance.code
    data['name'] = instance.name
    return data


# Данные об организации
def make_organization_data(instance):

    data = dict()
    data['code'] = instance.code
    data['name'] = instance.name
    return data


# Данные о клиенте
def make_headquater_data(instance):

    data = dict()
    data['code'] = instance.code
    data['name'] = instance.name
    data['prefix'] = instance.prefix
    return data


# Данные о претензии
def make_claim_data(instance):

    data = dict()
    data['id'] = instance.id
    data['number'] = instance.number
    data['type'] = instance.claim_type.name
    data['text'] = instance.text
    data['user_name'] = instance.user_name
    data['dt_created'] = instance.dt_created.isoformat()
    data['dt_updated'] = instance.dt_updated.isoformat()
    if instance.dt_status_changed:
        data['dt_status_changed'] = instance.dt_status_changed.isoformat()
    return data


# данные о сообщении по претензии
def make_message_data(instance):

    data = dict()
    data['party'] = instance.party
    data['text'] = instance.text
    data['user_name'] = instance.user_name
    data['dt_created'] = instance.dt_created.isoformat()
    return data


def make_notifications(users, emails, template, data):

    # Если передан список пользователей
    for user in users:
        if not user.email:
            continue
        # Создаем объект уведомления
        NotifyItem.objects.create(email=user.email, full_name=user.get_full_name(), template_slug=template,
                                  params=data)
    # Если передан список email
    for email in emails:
        if not email['email']:
            continue
        # Создаем объект уведомления
        NotifyItem.objects.create(email=email['email'], full_name=email['full_name'], template_slug=template,
                                  params=data)
