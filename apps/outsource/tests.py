from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db.models import Q
from rest_framework.test import APITestCase

import json
from datetime import date, timedelta
from django.utils import timezone

from apps.outsource.models import User, Job, Agency, Organization, Headquater
from apps.permission.models import AccessProfile, AccessRole
from apps.employees.models import AgencyEmployee, OrgHistory, JobHistory, EmployeeEvent
from apps.shifts.models import OutsourcingRequest, OutsourcingShift
from apps.lib.utils import content_type_ids_for_models

# from .test_data_generator import *

"""
Документация к API:
https://github.com/wfmexpert/outsourcing/wiki/DEV.-HTTP-API
"""


class AgencyEmployeeAgeTest(TestCase):

    fixtures = ['headquater', 'agency', 'agency_employee']

    def test_agency_employee_18(self):
        """
        Проверка массива сотрудников на зрелость при приеме на работу
        """
        violation_count = 0
        employees_list = AgencyEmployee.objects.all().order_by('id')
        for employee in employees_list:
            violation_count += self.validate_date_of_birth(employee)
        # Проверка условия
        self.assertEqual(violation_count, 0, 'Количество нарушений должно быть 0')

    @staticmethod
    def validate_date_of_birth(employee):
        """
        Проверяет что сотруднику 18+ лет.
        """
        years = employee.receipt.year - employee.date_of_birth.year

        new_year_day_birth = date(year=employee.date_of_birth.year, month=1, day=1)
        new_year_day_receipt = date(year=employee.receipt.year, month=1, day=1)
        birth_day_of_year = (employee.date_of_birth - new_year_day_birth).days + 1
        receipt_day_of_year = (employee.receipt - new_year_day_receipt).days + 1

        if not ((birth_day_of_year <= receipt_day_of_year and years == 18) or years > 18):
            return 1
        return 0


class ApiBaseSuperTest(APITestCase):
    # Заполнение БД
    fixtures = ['headquater', 'organization', 'agency', 'job',
                'outsourcing_request', 'outsourcingshift',
                'agency_employee', 'orghistory', 'jobhistory']

    def test_get(self, **kwargs):
        kwargs.setdefault('agency_id', 1)

        """Создание пользователя и проверка логина"""
        # Создаем тестового суперпользователя
        User.objects.create_superuser(username='test_user', password='test_pass', email='test@test.test')
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """Расчет количества объектов для Агентства"""
        # Считаем количество заявок, которые должны попасть в выдачу Агентства
        out_requests = OutsourcingRequest.objects.filter(agency_id=1)
        # Считаем количество смен, которые должны попасть в выдачу Агентства
        out_shifts = OutsourcingShift.objects.filter(agency_id=1, state='accept')
        # Считаем количество сотрудников, которые должны попасть в выдачу Агентства
        agency_employees = AgencyEmployee.objects.filter(agency_id=1)

        """Проверка заявок от Агентства"""
        # Делаем запрос к API (список заявок)
        response = self.client.get(reverse('api_requests_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        response = response.json()
        # Сравниваем размер массива
        self.assertEqual(len(list(response['data'])), len(out_requests), 'Массивы заявок Агентства не совпадают')

        """Проверка смен от Агентства"""
        # Делаем запрос к API (список смен)
        response = self.client.get(reverse('api_shifts_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data['data']), len(out_shifts), 'Массивы смен Агентства не совпадают')

        """Проверка сотрудников от Агентства"""
        # Делаем запрос к API (список сотрудников)
        response = self.client.get(reverse('api_employee_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data['data']), len(agency_employees),
                         'Массивы сотрудников Агентства не совпадают')

        """Сброс параметров для тестирования относительно Клиента"""
        # Очищаем параметры
        kwargs.clear()
        # устанавливаем параметры для Клиента
        kwargs.setdefault('headquater_id', 1)

        """Расчет количества объектов для Клиента"""
        # Считаем количество заявок, которые должны попасть в выдачу Клиента
        out_requests = OutsourcingRequest.objects.filter(headquater_id=1)
        # Считаем количество смен, которые должны попасть в выдачу Клиента
        out_shifts = OutsourcingShift.objects.filter(headquater_id=1, state='accept')
        # Считаем количество сотрудников, которые должны попасть в выдачу Клиента
        query_set = OrgHistory.objects.filter(headquater_id=1)
        query_set = query_set.filter(Q(start__lte=timezone.now().date()) &
                                     (Q(end__gte=timezone.now().date()) |
                                      Q(end__isnull=True))) \
            .order_by('agency_employee_id').distinct('agency_employee_id').values_list('agency_employee_id', flat=True)
        agency_employees = AgencyEmployee.objects.filter(id__in=query_set)

        """Проверка заявок от Клиента"""
        # Делаем запрос к API (список заявок)
        response = self.client.get(reverse('api_requests_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        response = response.json()
        # Сравниваем размер массива
        self.assertEqual(len(list(response['data'])), len(out_requests), 'Массивы заявок Клиента не совпадают')

        """Проверка смен от Клиента"""
        # Делаем запрос к API (список смен)
        response = self.client.get(reverse('api_shifts_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data['data']), len(out_shifts), 'Массивы смен Клиента не совпадают')

        """Проверка сотрудников от Клиента"""
        # Делаем запрос к API (список сотрудников)
        response = self.client.get(reverse('api_employee_list_headquater'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data['data']), len(agency_employees), 'Массивы сотрудников Клиента не совпадают')

    def test_add_change(self, **kwargs):
        kwargs.setdefault('agency_id', 1)

        """Создание пользователя и проверка логина"""
        # Создаем тестового суперпользователя
        User.objects.create_superuser(username='test_user', password='test_pass', email='test@test.test')
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """Получение сотрудника"""
        # Делаем запрос к API (список сотрудников)
        response = self.client.get(reverse('api_employee_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertGreater(len(response.data['data']), 0, 'Массивы сотрудников пустой')
        # Получили ID сотрудника
        employee_id = response.data['data'][0]['id']

        """Проверка списка функций"""
        job_history = JobHistory.objects.filter(agency_employee_id=employee_id)
        # Делаем запрос к API (получение списка функций)
        response = self.client.get(reverse('api_job_history'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data), len(job_history), 'Массивы функций не совпадают')

        """Удаление функций"""
        # Берем первое назначение
        job_history_new = job_history.first()
        # И удаляем его
        response = self.client.post(reverse('api_delete_job_history'), {'job_history_id': job_history_new.id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 204, 'Некорректный код ответа')
        # Сравниваем размеры массивов функций
        len_new = len(JobHistory.objects.filter(agency_employee_id=employee_id))
        self.assertNotEqual(len(job_history), len_new, 'Список функций не изменился')
        # Проверяем что изменения применились
        response = self.client.get(reverse('api_job_history'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data), len_new, 'Массивы функций не совпадают')

        """Добавление функций"""
        # Добавляем функцию в доступные агентству
        job = Job.objects.all().first()
        agency = Agency.objects.filter(id=1).first()
        agency.jobs.add(job)

        # Готовим переменные для назначения функций
        kwargs.clear()
        kwargs.setdefault('employee_id', employee_id)
        kwargs.setdefault('agency_employee_id', employee_id)
        kwargs.setdefault('job_id', job.id)
        kwargs.setdefault('start', timezone.now().date().isoformat())

        # Делаем запрос к API (назначение функции)
        response = self.client.post(reverse('api_job_history'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 201, 'Некорректный код ответа')
        # Проверяем что изменения применились
        response = self.client.get(reverse('api_job_history'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размеры массивов функций
        len_new = len(JobHistory.objects.filter(agency_employee_id=employee_id))
        self.assertEqual(len(response.data), len_new, 'Массивы функций не совпадают')

        """Проверка списка назначений к клиенту"""
        org_history = OrgHistory.objects.filter(agency_employee_id=employee_id)
        # Делаем запрос к API (назначение к клиентам)
        response = self.client.get(reverse('api_org_histories'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data), len(org_history), 'Массивы назначений не совпадают')

        """Отправка запроса на прием к клиенту"""
        organization = Organization.objects.all().first()
        # Готовим переменные для назначения к клиенту
        kwargs.clear()
        kwargs.setdefault('organization_id', organization.id)
        kwargs.setdefault('employee_list', json.dumps([employee_id]))
        kwargs.setdefault('recruitment_date', timezone.now().date().isoformat())

        response = self.client.post(reverse('api_set_employee_recruitment_event'), kwargs)

        # Сравниваем код ответа
        self.assertEqual(response.status_code, 201, 'Некорректный код ответа')
        org_history = org_history.filter(headquater_id=organization.headquater.id, end__isnull=True)

        # Если не существовало открытого OrgHistory то должно было добавитсья событие
        events = EmployeeEvent.objects.filter(agency_employee_id=employee_id,
                                              kind='recruitment',
                                              recruitment_date=timezone.now().date())
        if len(org_history) == 0:
            self.assertEqual(len(events), 1, 'Кадровое мероприятие приема отстутствует')
        else:
            self.assertEqual(len(events), 0, 'Создалось кадровое мероприятие приема')

        """Отправка запроса на увольнение от клиента"""
        # Проверяем наличие открытых OrgHistory
        org_hist = len(OrgHistory.objects.filter(agency_employee_id=employee_id,
                                                 start__isnull=False,
                                                 end__isnull=True,
                                                 headquater_id=org_history.first().headquater_id))

        # Готовим переменные для увольнения от клиента
        kwargs.clear()
        kwargs.setdefault('headquater_id', org_history.first().headquater_id)
        kwargs.setdefault('employee_list', json.dumps([employee_id]))
        kwargs.setdefault('dismissal_reason', 'Причина увольнения')
        kwargs.setdefault('dismissal_date', timezone.now().date().isoformat())

        # Отправляем запрос на увольнение от клиента
        response = self.client.post(reverse('api_set_employee_dismissal_event'), kwargs)

        # Сравниваем код ответа
        self.assertEqual(response.status_code, 201, 'Некорректный код ответа')
        events = EmployeeEvent.objects.filter(agency_employee_id=employee_id, kind='dismissal',
                                              dismissal_date=timezone.now().date(),
                                              headquater_id=org_history.first().headquater_id)
        self.assertEqual(len(events), 1, 'Кадровое мероприятие увольнения отстутствует')

        # Если были открытые OrgHistory то проверяем, что они закрываются и создаются кадроывве мероприятия
        if org_hist > 0:
            org_hist_upd = len(OrgHistory.objects.filter(agency_employee_id=employee_id,
                                                         start__isnull=False,
                                                         end=timezone.now().date() - timedelta(days=1),
                                                         headquater_id=org_history.first().headquater_id))
            # Если были открытые OrgHistory, то они должны были закрыться
            self.assertEqual(org_hist, org_hist_upd, 'OrgHistory были, но не закрылись')
            # Должны были создаться кадровые мероприятия по количеству OrgHistory
            events = EmployeeEvent.objects.filter(agency_employee_id=employee_id,
                                                  kind='dismissal',
                                                  dismissal_date=timezone.now().date(),
                                                  headquater_id=org_history.first().headquater_id)
            self.assertEqual(len(events), org_hist,
                             'Количество кадровых мероприятий не соответствует количеству ранее открытых OrgHistory')

        # Проверяем внутренние мероприятия отдаются по API
        events = EmployeeEvent.objects.filter(Q(agency_employee_id=employee_id) &
                                              Q(recruitment_date=timezone.now().date()) |
                                              Q(dismissal_date=timezone.now().date()))
        response = self.client.get(reverse('api_employee_events'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data), len(events), 'Массивы мероприятий не совпадают')

        """Увольнение сотрудника"""
        # Проверяем наличие открытых OrgHistory
        org_hist = len(OrgHistory.objects.filter(agency_employee_id=employee_id,
                                                 start__isnull=False,
                                                 end__isnull=True))

        # Готовим переменные для увольнения сотрудника
        kwargs.clear()
        kwargs.setdefault('employee_list', json.dumps([employee_id]))
        kwargs.setdefault('dismissal_reason', 'Причина увольнения')
        kwargs.setdefault('dismissal_date', timezone.now().date().isoformat())

        response = self.client.post(reverse('api_dismiss_employee'), kwargs)

        # Сравниваем код ответа
        self.assertEqual(response.status_code, 204, 'Некорректный код ответа')

        # Если были открытые OrgHistory то проверяем, что они закрываются и создаются кадроывве мероприятия
        if org_hist > 0:
            org_hist_upd = len(OrgHistory.objects.filter(agency_employee_id=employee_id,
                                                         start__isnull=False,
                                                         end__isnull=True))
            # Если были открытые OrgHistory, то они должны были закрыться
            self.assertGreater(org_hist, org_hist_upd, 'OrgHistory были, но не закрылись')
            # Должны были создаться кадровые мероприятия по количеству OrgHistory
            events = EmployeeEvent.objects.filter(agency_employee_id=employee_id,
                                                  kind='dismissal',
                                                  dismissal_date=timezone.now().date())
            self.assertEqual(len(events), org_hist,
                             'Количество кадровых мероприятий не соответствует количеству ранее открытых OrgHistory')

        # Проверяем, что установилась дата увольнения
        emp = AgencyEmployee.objects.filter(id=employee_id).first()
        self.assertEqual(emp.dismissal, timezone.now().date(), 'Дата увольнения не установлена')

        ###
        # TODO Снятие назначений с OutsourcingShift
        # сначала надо сгенерировать смены
        ###

        events = EmployeeEvent.objects.filter(agency_employee_id=employee_id, kind='dismissal',
                                              dismissal_date=timezone.now().date())
        self.assertEqual(len(events), 1, 'Кадровое мероприятие увольнения отстутствует')

        # Проверяем внутренние мероприятия отдаются по API
        events = EmployeeEvent.objects.filter(Q(agency_employee_id=employee_id) &
                                              Q(recruitment_date=timezone.now().date()) |
                                              Q(dismissal_date=timezone.now().date()))
        response = self.client.get(reverse('api_employee_events'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data), len(events), 'Массивы мероприятий не совпадают')


class ApiGetShiftEmployee(APITestCase):
    fixtures = [
        'organization', 'job', 'agency_employee', 'headquater', 'agency',
        'orghistory', 'jobhistory', 'outsourcing_request', 'outsourcingshift', 'orglink'
    ]

    """Получение сотрудников на смену к которой должен быть доступ у Агентства"""
    def test_get_own(self):
        """Создание пользователя и проверка логина"""
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        # Выбираем смену
        shift_own = OutsourcingShift.objects.filter(agency_id=1).first()

        # Делаем GET запрос к API на получение смены к которой должен быть доступ
        response = self.client.get(reverse('api_shift_employee'), {'shift_id': shift_own.id})

        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')

    """Получение сотрудников на смену к которой не должно быть доступа у Агентства"""
    def test_get_foreign(self):
        """Создание пользователя и проверка логина"""
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        shift_foreign = OutsourcingShift.objects.exclude(agency_id=1).first()
        # Делаем GET запрос к API на получение смены к которой не должно быть доступа
        response = self.client.get(reverse('api_shift_employee'), {'shift_id': shift_foreign.id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 400, 'Некорректный код ответа')

    """Назначение и переназначение на смену к которой должен быть доступ у Агентства"""
    def test_set_own(self, **kwargs):
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        shift = OutsourcingShift.objects.filter(agency_id=1, agency_employee__isnull=True).first()
        emp = AgencyEmployee.objects.filter(agency_id=1, jobhistory__job_id=shift.job.id).first()

        kwargs.update({
            'agency_employee_id': emp.id,  # id сотрудника
            'id': shift.id  # id смены
        })

        # Назначаем сотрудника на смену
        response = self.client.post(reverse('api_shift_employee'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 201, 'Некорректный код ответа')

        # Проверяем, что сотрудник назначен на смену
        shift_updated = OutsourcingShift.objects.get(id=shift.id)
        self.assertEqual(shift_updated.agency_employee.id, emp.id, "Сотрудник не назначен на смену")

        # Проверяем переназначение сотрудника
        emp = AgencyEmployee.objects.filter(agency_id=1, jobhistory__job_id=shift.job.id).exclude(id=emp.id).first()

        if emp:
            kwargs.update({
                'agency_employee_id': emp.id,  # id сотрудника
                'id': shift.id  # id смены
            })

            # Переназначем сотрудника на смену
            response = self.client.post(reverse('api_shift_employee'), kwargs)
            # Сравниваем код ответа
            self.assertEqual(response.status_code, 201, 'Некорректный код ответа')
            # Проверяем, что сотрудник переназначен на смену
            shift_updated2 = OutsourcingShift.objects.get(id=shift.id)
            self.assertNotEqual(shift_updated2.agency_employee.id, shift_updated.agency_employee.id,
                                "Сотрудник не изменился")

        """Назначение и переназначение на смену к которой не должно быть доступа у Агентства"""
    def test_set_foreign(self, **kwargs):
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        shift = OutsourcingShift.objects.filter(agency_employee__isnull=True).exclude(agency_id=1).first()
        emp = AgencyEmployee.objects.filter(jobhistory__job_id=shift.job.id).exclude(agency_id=1).first()

        kwargs.update({
            'agency_employee_id': emp.id,  # id сотрудника
            'id': shift.id  # id смены
        })

        # Назначаем сотрудника на смену
        response = self.client.post(reverse('api_shift_employee'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 400, 'Некорректный код ответа')

        # Проверяем, что сотрудник не назначен на смену
        shift_updated = OutsourcingShift.objects.get(id=shift.id)
        self.assertEqual(shift_updated.agency_employee, shift.agency_employee, "Сотрудник назначен на смену")

        # Проверяем переназначение сотрудника
        shift = OutsourcingShift.objects.filter(agency_employee__isnull=False).exclude(agency_id=1).first()
        emp = AgencyEmployee.objects.filter(agency_id=1, jobhistory__job_id=shift.job.id).exclude(id=emp.id).first()

        if emp:
            kwargs.update({
                'agency_employee_id': emp.id,  # id сотрудника
                'id': shift.id  # id смены
            })

            # Переназначем сотрудника на смену
            response = self.client.post(reverse('api_shift_employee'), kwargs)
            # Сравниваем код ответа
            self.assertEqual(response.status_code, 400, 'Некорректный код ответа')
            # Проверяем, что сотрудник не переназначен на смену
            shift_updated2 = OutsourcingShift.objects.get(id=shift.id)
            self.assertEqual(shift_updated2.agency_employee, shift.agency_employee, "Сотрудник изменился")


"""Проверка количества передаваемых заявок"""


class ApiGetOutRequests(APITestCase):
    fixtures = [
        'outsourcing_request', 'headquater', 'organization', 'agency'
    ]

    def test_get_requests_agency(self, **kwargs):
        kwargs.setdefault('agency_id', 1)
        """Создание пользователя и проверка логина"""
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """Проверка заявок от Агентства"""
        # Считаем количество заявок, которые должны попасть в выдачу Агентства
        out_requests = OutsourcingRequest.objects.filter(agency_id=1)
        # Делаем GET запрос к API (список заявок)
        response = self.client.get(reverse('api_requests_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        response = response.json()
        # Сравниваем размер массива
        self.assertEqual(len(list(response['data'])), len(out_requests), 'Массивы заявок Агентства не совпадают')

    def test_get_requests_headquater(self, **kwargs):
        kwargs.setdefault('headquater_id', 1)
        """Создание пользователя и проверка логина"""
        create_user(headquaters=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """Проверка заявок от Клиента"""
        # Считаем количество заявок, которые должны попасть в выдачу Агентства
        out_requests = OutsourcingRequest.objects.filter(headquater_id=1)
        # Делаем GET запрос к API (список заявок)
        response = self.client.get(reverse('api_requests_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        response = response.json()
        # Сравниваем размер массива
        self.assertEqual(len(list(response['data'])), len(out_requests), 'Массивы заявок Клиента не совпадают')


"""Проверка количества передаваемых смен"""


class ApiGetOutShifts(APITestCase):
    fixtures = [
        'outsourcingshift', 'outsourcing_request', 'headquater', 'organization', 'agency', 'job', 'agency_employee'
    ]

    def test_get_shifts_agency(self, **kwargs):
        kwargs.setdefault('agency_id', 1)
        """Создание пользователя и проверка логина"""
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """Проверка смен от Агентства"""
        # Считаем количество смен, которые должны попасть в выдачу Агентства
        out_shifts = OutsourcingShift.objects.filter(agency_id=1, state='accept')
        # Делаем запрос к API (список смен)
        response = self.client.get(reverse('api_shifts_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data['data']), len(out_shifts), 'Массивы смен Агентства не совпадают')

    def test_get_shifts_headquater(self, **kwargs):
        kwargs.setdefault('headquater_id', 1)
        """Создание пользователя и проверка логина"""
        create_user(headquaters=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """Проверка смен от Клиента"""
        # Считаем количество смен, которые должны попасть в выдачу Клиента
        out_shifts = OutsourcingShift.objects.filter(headquater_id=1, state='accept')
        # Делаем запрос к API (список смен)
        response = self.client.get(reverse('api_shifts_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data['data']), len(out_shifts), 'Массивы смен Клиента не совпадают')


"""
Проверка количества передаваемых сотрудников
Проверка доступа к своим/чужим сотрудникам
Исходные данные для проверки доступа берутся из БД
"""


class ApiGetAgencyEmployees(APITestCase):
    fixtures = [
        'headquater', 'organization', 'agency', 'agency_employee', 'orghistory',
    ]

    """Получение списка сотрудников Агентством"""
    def test_get_employees_list_agency(self, **kwargs):
        kwargs.setdefault('agency_id', 1)
        """Создание пользователя и проверка логина"""
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """Проверка сотрудников от Агентства"""
        # Считаем количество сотрудников, которые должны попасть в выдачу Агентства
        agency_employees = AgencyEmployee.objects.filter(agency_id=1)
        # Делаем запрос к API (список сотрудников)
        response = self.client.get(reverse('api_employee_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data['data']), len(agency_employees),
                         'Массивы сотрудников Агентства не совпадают')

    """Получение списка сотрудников Клиентом"""
    def test_get_employees_list_headquater(self, **kwargs):
        kwargs.setdefault('headquater_id', 1)
        """Создание пользователя и проверка логина"""
        create_user(headquaters=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """Проверка сотрудников от Клиента"""
        # Считаем количество сотрудников, которые должны попасть в выдачу Клиента
        query_set = OrgHistory.objects.filter(headquater_id=1)
        query_set = query_set.filter(Q(start__lte=timezone.now().date()) &
                                     (Q(end__gte=timezone.now().date()) |
                                      Q(end__isnull=True))) \
            .order_by('agency_employee_id').distinct('agency_employee_id').values_list('agency_employee_id', flat=True)
        agency_employees = AgencyEmployee.objects.filter(id__in=query_set)
        # Делаем GET запрос к API (список сотрудников), передавая параметры
        response = self.client.get(reverse('api_employee_list_headquater'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data['data']), len(agency_employees), 'Массивы сотрудников Клиента не совпадают')

    """Получение сотрудника к которому должен быть доступ Агентством"""
    def test_get_own_agency(self):
        """Создание пользователя и проверка логина"""
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        # Выбираем сотрудника
        emp = AgencyEmployee.objects.filter(agency_id=1).first()

        # Делаем GET запрос к API на получение сотрудника, к которому должен быть доступ
        response = self.client.get(reverse('api_employee'), {'employee_id': emp.id})

        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')

    """Получение сотрудника к которому не должно быть доступа Агентством"""
    def test_get_employee_foreign_agency(self):
        """Создание пользователя и проверка логина"""
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        # Выбираем сотрудника
        emp = AgencyEmployee.objects.exclude(agency_id=1).first()

        # Делаем GET запрос к API на получение сотрудника, к которому должен быть доступ
        response = self.client.get(reverse('api_employee'), {'employee_id': emp.id})

        # Сравниваем код ответа
        self.assertEqual(response.status_code, 400, 'Некорректный код ответа')

    """Получение сотрудника к которому должен быть доступ Клиентом"""
    def test_get_employee_own_headquater(self):
        """Создание пользователя и проверка логина"""
        create_user(headquaters=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        # Выбираем сотрудника
        emp = AgencyEmployee.objects.filter(orghistory__headquater_id=1).first()

        # Делаем GET запрос к API на получение сотрудника, к которому должен быть доступ
        response = self.client.get(reverse('api_employee'), {'employee_id': emp.id})

        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')

    """Получение сотрудника к которому не должно быть доступа Клиентом"""
    def test_get_employee_foreign_headquater(self):
        """Создание пользователя и проверка логина"""
        create_user(headquaters=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        # Выбираем сотрудника
        emp = AgencyEmployee.objects.exclude(orghistory__headquater_id=1).first()

        # Делаем GET запрос к API на получение сотрудника, к которому должен быть доступ
        response = self.client.get(reverse('api_employee'), {'employee_id': emp.id})

        # Сравниваем код ответа
        self.assertEqual(response.status_code, 400, 'Некорректный код ответа')


"""
Проверка данных по сотруднику (кадровые мероприятия, назначения к клиенту)
Все данные (в том числе исходные для тестов) получаются на основе ответов по API
"""


class ApiGetAgencyEmployeeInfo(APITestCase):
    fixtures = [
        'headquater', 'organization', 'agency', 'agency_employee', 'orghistory', 'employeeevent', 'auth_user'
    ]

    def test_get_employee_agency(self, **kwargs):
        kwargs.setdefault('agency_id', 1)
        """Создание пользователя и проверка логина"""
        create_user(agencies=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """"Получение сотрудника"""
        # Делаем GET запрос к API (список сотрудников), передавая параметры
        response = self.client.get(reverse('api_employee_list'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertGreater(len(response.data['data']), 0, 'Массив сотрудников пустой')
        # Получили ID сотрудника
        employee_id = response.data['data'][0]['id']

        """Проверка списка назначений к клиенту"""
        org_history = OrgHistory.objects.filter(agency_employee_id=employee_id)
        response = self.client.get(reverse('api_org_histories'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data), len(org_history), 'Массивы назначений Агентства не совпадают')

        """Проверяем мероприятия"""
        events = EmployeeEvent.objects.filter(agency_employee_id=employee_id)
        response = self.client.get(reverse('api_employee_events'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data), len(events), 'Массивы мероприятий Агентства не совпадают')

    def test_get_employee_headquater(self, **kwargs):
        kwargs.setdefault('headquater_id', 1)
        """Создание пользователя и проверка логина"""
        create_user(headquaters=[1])
        # Проверяем что пользователю удалось залогиниться
        self.assertTrue(self.client.login(email='test_user', password='test_pass'))

        """"Получение сотрудника"""
        # Делаем запрос к API (список сотрудников)
        response = self.client.get(reverse('api_employee_list_headquater'), kwargs)
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertGreater(len(response.data['data']), 0, 'Массив сотрудников пустой')
        # Получили ID сотрудника
        employee_id = response.data['data'][0]['id']

        """Проверка списка назначений к клиенту"""
        org_history = OrgHistory.objects.filter(agency_employee_id=employee_id, headquater_id=1)
        response = self.client.get(reverse('api_org_histories'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data), len(org_history), 'Массивы назначений Клиента не совпадают')

        """Проверяем мероприятия"""
        events = EmployeeEvent.objects.filter(agency_employee_id=employee_id, headquater_id=1)
        response = self.client.get(reverse('api_employee_events'), {'employee_id': employee_id})
        # Сравниваем код ответа
        self.assertEqual(response.status_code, 200, 'Некорректный код ответа')
        # Сравниваем размер массива
        self.assertEqual(len(response.data), len(events), 'Массивы мероприятий Клиента не совпадают')


"""
Метод создания AccessProfile объектов 
В kwargs:
    agencies - список id агентств, котормым назначить сотрудника, например [1, 2, 6]
    headquaters - список id клиентов, котормым назначить сотрудника, например [1, 2, 6]
"""


def create_user(**kwargs):
    user = User.objects.create_user(username='test_user', password='test_pass')
    if kwargs.get("agencies"):
        unit_type_id = content_type_ids_for_models(Agency)[0]
        role = AccessRole.objects.filter(party='agency').first()
        for ag_id in kwargs["agencies"]:
            agency = Agency.objects.filter(id=ag_id).first()
            AccessProfile.objects.create(user=user, unit_type_id=unit_type_id, unit_id=ag_id, role=role, headquater_id=agency.headquater.id)
    if kwargs.get("headquaters"):
        unit_type_id = content_type_ids_for_models(Organization)[0]
        role = AccessRole.objects.filter(party='client').first()
        for hq_id in kwargs["headquaters"]:
            organization = Organization.objects.filter(headquater_id=hq_id, kind='head').first()
            AccessProfile.objects.create(user=user, unit_type_id=unit_type_id, unit_id=organization.id, role=role, headquater_id=hq_id)
