#
# Copyright 2018 ООО «Верме»
#
# Файл создания объектов OrgHistory в ручном режиме,
# на основе созданных событий EmployeeEvent
#

# coding=utf-8;

from django.core.management.base import BaseCommand
from apps.employees.models import AgencyEmployee, EmployeeEvent, OrgHistory


class Command(BaseCommand):
    help = 'Creates OrgHistory objects from EmployeeEvents'

    def handle(self, *args, **options):
        employees_list = AgencyEmployee.objects.all()
        for employee in employees_list:
            events_list = EmployeeEvent.objects.filter(agency_employee=employee, kind='recruitment')
            for event in events_list:
                org_history_count = OrgHistory.objects.filter(agency_employee=employee, headquater=event.headquater, organization=event.organization).count()
                if org_history_count == 0:
                    OrgHistory.objects.create(agency_employee=employee, organization=event.organization,
                                          start=event.recruitment_date, end=None, number=employee.number, headquater=event.headquater)

        print('Orghistory created for all agency_employees')
