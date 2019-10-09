#
# Copyright 2018 ООО «Верме»
#
# Файл проверки объектов AgencyEmployee в ручном режиме,
# на предмет возраста сотрудника на момент приема
#

# coding=utf-8;

from django.core.management.base import BaseCommand
from apps.employees.models import AgencyEmployee
from datetime import date

class Command(BaseCommand):
    help = 'Checks AgencyEmployee objects'

    def handle(self, *args, **options):
        violation_count = 0
        employees_list = AgencyEmployee.objects.all().order_by('id')
        for employee in employees_list:
            violation_count += Command.validate_date_of_birth(employee)
        print('Successfully checked all AgencyEmployee')
        print('Violation count', violation_count)

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
            print('Violation - AgencyEmployee ID', employee.id, 'date_of_birth', employee.date_of_birth, 'receipt', employee.receipt)
            return 1
        return 0