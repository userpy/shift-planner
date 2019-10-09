import os

from collections import OrderedDict
from django.conf import settings
from django.core.files import File
from django.core.management import BaseCommand
from django.core.management import call_command

from apps.permission.models import Page

INITIAL_DATA = OrderedDict([
    ("permission_pages", [
        {"name": "Сотрудники", "code": "employees_list", "icon": "user-circle", "party": "agency", "sort_key": 1,
         "ext_name": "Сотрудники"},
        {"name": "Заявки", "code": "requests_list", "icon": "list-alt", "party": "agency", "sort_key": 2,
         "ext_name": "Рассмотрение заявок на персонал"},
        {"name": "Смены", "code": "shifts_list", "icon": "users", "party": "agency", "sort_key": 3,
         "ext_name": "Назначение сотрудников на смены"},
        {"name": "Претензии", "code": "claims_list", "icon": "exclamation", "party": "agency", "sort_key": 4,
         "ext_name": "Список претензий"},

        {"name": "Создание сотрудника", "code": "create_employee", "party": "agency", "sort_key": 5,
         "ext_name": "Создание сотрудника"},
        {"name": "Редактирование сотрудника", "code": "edit_employee", "party": "agency", "sort_key": 6,
         "ext_name": "Редактирование сотрудника"},
        {"name": "Просмотр смен", "code": "shifts_confirm", "party": "agency", "sort_key": 7,
         "ext_name": "Просмотр и подтверждение смен"},
        {"name": "Просмотр претензии", "code": "claim", "party": "agency", "sort_key": 8,
         "ext_name": "Просмотр претензии"},

        {"name": "Сотрудники", "code": "hq_employees_list", "icon": "user-circle", "party": "client", "sort_key": 11,
         "ext_name": "Сотрудники"},
        {"name": "Заявки", "code": "hq_requests_list", "icon": "list-alt", "party": "client", "sort_key": 12,
         "ext_name": "Заявки на персонал"},
        {"name": "Смены", "code": "hq_shifts_list", "icon": "users", "party": "client", "sort_key": 13,
         "ext_name": "Смены"},
        {"name": "Претензии", "code": "hq_claims_list", "icon": "exclamation", "party": "client", "sort_key": 14,
         "ext_name": "Список претензий"},

        {"name": "Редактирование сотрудника", "code": "hq_edit_employee", "party": "client", "sort_key": 15,
         "ext_name": "Редактирование сотрудника"},
        {"name": "Просмотр смен", "code": "hq_shifts_confirm", "party": "client", "sort_key": 16,
         "ext_name": "Просмотр и подтверждение смен"},
        {"name": "Просмотр претензии", "code": "hq_claim", "party": "client", "sort_key": 17,
         "ext_name": "Просмотр претензии"},

        {"name": "Сотрудники", "code": "promo_employees_list", "icon": "user-circle", "party": "promo", "sort_key": 21,
         "ext_name": "Сотрудники"},
        {"name": "Претензии", "code": "promo_claims_list", "icon": "exclamation", "party": "promo", "sort_key": 24,
         "ext_name": "Список претензий"},

        {"name": "Создание сотрудника", "code": "promo_create_employee", "party": "promo", "sort_key": 25,
         "ext_name": "Создание сотрудника"},
        {"name": "Редактирование сотрудника", "code": "promo_edit_employee", "party": "promo", "sort_key": 26,
         "ext_name": "Редактирование сотрудника"},
        {"name": "Просмотр претензии", "code": "promo_claim", "party": "promo", "sort_key": 28,
         "ext_name": "Просмотр претензии"},

        {"name": "Сотрудники", "code": "broker_employees_list", "icon": "user-circle", "party": "broker", "sort_key": 29,
         "ext_name": "Сотрудники"},
        {"name": "Претензии", "code": "broker_claims_list", "icon": "exclamation", "party": "broker", "sort_key": 30,
         "ext_name": "Список претензий"},

        {"name": "Создание сотрудника", "code": "broker_create_employee", "party": "broker", "sort_key": 31,
         "ext_name": "Создание сотрудника"},
        {"name": "Редактирование сотрудника", "code": "broker_edit_employee", "party": "broker", "sort_key": 32,
         "ext_name": "Редактирование сотрудника"},
        {"name": "Просмотр претензии", "code": "broker_claim", "party": "broker", "sort_key": 33,
         "ext_name": "Просмотр претензии"},
    ]),
])


class Command(BaseCommand):

    help = 'Filling the database, skipping existing rows'

    def add_arguments(self, parser):
        parser.add_argument(
            '--overwrite',
            action='store_true',
            default=False,
            help='Overwrite existing rows (if any)'
        )

    def handle(self, *args, **options):
        self._load_initial_data(options['overwrite'])

    def _load_initial_data(self, overwrite):
        for name, data in INITIAL_DATA.items():
            print('Syncing %s...' % name.replace('_', ' '))
            count = getattr(self, 'fill_' + name)(data, overwrite)
            print('Done, %d row(s) inserted' % count)

    def _simple_fill(self, Model, data, key, overwrite, params_func=None):
        count = 0
        for params in data:
            try:
                obj = Model.objects.get(**{key: params[key]})
                if not overwrite:
                    continue
            except Model.DoesNotExist:
                obj = Model()

            if params_func is None:
                for attr, value in params.items():
                    setattr(obj, attr, value)
            else:
                params_func(obj, params)
            obj.save()
            count += 1
        return count

    def fill_permission_pages(self, data, overwrite):
        return self._simple_fill(Page, data, 'code', overwrite)
