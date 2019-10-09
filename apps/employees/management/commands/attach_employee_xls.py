from django.core.management.base import BaseCommand
import xlrd
from apps.employees.methods import attach_employee
import datetime
from django.contrib.auth.models import User
from apps.outsource.models import Organization, Agency
from apps.employees.models import AgencyEmployee


class Command(BaseCommand):
    help = 'Прикрепление пользователя к городу'

    def handle(self, *args, **options):
        book = xlrd.open_workbook('/tmp/emp.xls')
        sheet = book.sheet_by_index(0)
        user = User.objects.get(pk=1)
        for i in range(1, sheet.nrows):
            date = datetime.datetime(*xlrd.xldate_as_tuple(sheet.cell_value(i, 16), book.datemode)).date()
            try:
                agency = Agency.objects.get(code=str(sheet.cell_value(i, 7)).replace('.0', ''))
            except Agency.DoesNotExist:
                print(f"Отсутствует агенство {sheet.cell_value(i, 7)}")
                continue
            try:
                employee = AgencyEmployee.objects.get(number=sheet.cell_value(i, 0), agency=agency)
            except AgencyEmployee.DoesNotExist:
                print(f"Отсутствует сотрудник {sheet.cell_value(i, 0)}")
                continue
            except:
                print(f"Дубликат сотрудника {sheet.cell_value(i, 0)}")
                continue
            try:
                org = Organization.objects.get(code=sheet.cell_value(i, 11))
            except Organization.DoesNotExist:
                print(f"Отсутствует организация {sheet.cell_value(i, 11)}")
                continue
            if not attach_employee(user=user, employee=employee, recruitment_date=date, organization=org):
                print(f"Не добавился {sheet.cell_value(i, 0)}")




