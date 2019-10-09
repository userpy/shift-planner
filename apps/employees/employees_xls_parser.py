"""
Copyright 2018 ООО «Верме»

Парсер записей модели Employee из XLS документов
"""

import datetime
import xlrd

from django.db import transaction
from django.db.models import Q

from apps.employees.models import OrgHistory, JobHistory, AgencyEmployee, EmployeeDoc, DocType
from apps.outsource.models import Headquater, Organization, Agency, Job
from collections import defaultdict


def name_or_code_q(name_or_code):
    return Q(name=name_or_code) | Q(code=name_or_code)


class EmployeesXLSParser:
    """
    Парсер xls-файла со списком сотрудников, импортируемых в Django-админке
    """

    def __init__(self):
        self.employee_data = {}
        self.processed_employees = set()
        self.created_employees_data = defaultdict(list)

    def parse(self, file_contents):
        rb = xlrd.open_workbook(file_contents=file_contents)
        sheet = rb.sheet_by_index(0)
        errors = []
        for rownum in range(1, sheet.nrows):
            row = sheet.row_values(rownum)
            try:
                self.employee_data = self.get_struct_from_row(row, rb)
                self.process_employee_data()
            except Exception as exc:
                errors.append({'rownum': rownum, 'exc': exc})

        return errors

    def process_employee_data(self):
        with transaction.atomic():
            try:
                employee = AgencyEmployee.objects.get(number=self.employee_data['number'],
                                                      agency__code=self.employee_data['agency'])
                self.update_employee(employee)
            except AgencyEmployee.DoesNotExist:
                employee = self.create_employee()
                self.created_employees_data[employee].append(self.employee_data)
            except Exception:
                raise
        self.processed_employees.add(employee)

    @staticmethod
    def get_struct_from_row(row, rb):
        def get_cell_date(cell):
            return str(cell).strip() and datetime.datetime(*xlrd.xldate_as_tuple(cell, rb.datemode)) or None

        def get_number(value):
            try:
                number = int(value)
                return str(number)
            except (TypeError, ValueError):
                return value

        def get_int_as_string(value):
            if isinstance(value, str):
                return value
            return str(int(value))

        def clean_value(value):
            if isinstance(value, (bytes, str)):
                if value:
                    if isinstance(value, bytes):
                        value = value.encode('utf-8')
                    value = value.strip().replace("'", '')
                else:
                    value = ''
            return value

        return {
            'number': get_int_as_string(clean_value(row[0])),
            'surname': clean_value(row[1]),
            'firstname': clean_value(row[2]),
            'patronymic': clean_value(row[3]),
            'gender': clean_value(row[4]),
            'date_of_birth': get_cell_date(clean_value(row[5])),
            'place_of_birth': clean_value(row[6]),
            'agency': get_int_as_string(clean_value(row[7])),
            'receipt': get_cell_date(clean_value(row[8])),
            'dismissal': get_cell_date(clean_value(row[9])),

            'org_history': {
                'head_code': get_int_as_string(clean_value(row[10])),
                'org_code': get_int_as_string(clean_value(row[11])),
                'number': get_int_as_string(clean_value(row[12])),
                'start_date': get_cell_date(clean_value(row[13])),
                'end_date': get_cell_date(clean_value(row[14])),
            },
            'job_history': {
                'job_code': get_int_as_string(clean_value(row[15])),
                'start_date': get_cell_date(clean_value(row[16])),
                'end_date': get_cell_date(clean_value(row[17])),
            },
            'doc': {
                'doc_code': get_int_as_string(clean_value(row[18])),
                'start_date': get_cell_date(clean_value(row[19])),
                'end_date': get_cell_date(clean_value(row[20])),
                'comments': clean_value(row[21]),
            }
        }

    def create_employee(self):
        agency = Agency.objects.get(code=self.employee_data['agency'])

        employee = AgencyEmployee()
        employee.surname = self.employee_data['surname']
        employee.firstname = self.employee_data['firstname']
        employee.patronymic = self.employee_data['patronymic']
        employee.number = self.employee_data['number']
        employee.gender = self.employee_data['gender']
        employee.date_of_birth = self.employee_data['date_of_birth']
        employee.place_of_birth = self.employee_data['place_of_birth']
        employee.receipt = self.employee_data['receipt']
        employee.dismissal = self.employee_data['dismissal']
        employee.agency = agency
        employee.save()

        self.create_job_history(employee=employee)
        self.create_doc(employee=employee)
        self.create_org_history(employee=employee)

        return employee

    def update_employee(self, employee):
        if self.employee_data['surname']:
            employee.surname = self.employee_data['surname']

        if self.employee_data['firstname']:
            employee.firstname = self.employee_data['firstname']

        if self.employee_data['patronymic']:
            employee.patronymic = self.employee_data['patronymic']

        if self.employee_data['gender']:
            employee.receipt_date = self.employee_data['gender']

        if self.employee_data['date_of_birth']:
            employee.date_of_birth = self.employee_data['date_of_birth']

        if self.employee_data['place_of_birth']:
            employee.place_of_birth = self.employee_data['place_of_birth']

        if self.employee_data['agency']:
            self.update_agency(employee)

        if self.employee_data['receipt']:
            employee.receipt = self.employee_data['receipt']

        if self.employee_data['dismissal']:
            employee.dismissal = self.employee_data['dismissal']

        if self.employee_data['job_history']['job_code']:
            self.update_or_create_job_history(employee)

        if self.employee_data['doc']['doc_code']:
            self.update_or_create_doc(employee)

        if self.employee_data['org_history']['org_code']:
            self.update_or_create_org_history(employee)

        employee.save()

    def update_agency(self, employee):
        agency = Agency.objects.get(code=self.employee_data['agency'])
        employee.agency = agency
        employee.save()

    def create_job_history(self, employee):
        job = Job.objects.get(code=self.employee_data['job_history']['job_code'])
        JobHistory.objects.create(agency_employee=employee,
                                  job=job,
                                  start=self.get_job_start_date(),
                                  end=self.get_job_end_date())

    def update_or_create_job_history(self, employee):
        job = Job.objects.get(code=self.employee_data['job_history']['job_code'])

        job_history = JobHistory.objects.filter(agency_employee_id=employee.id, job_id=job.id,
                                                start=self.get_job_start_date()).first()
        if job_history is None:
            self.create_job_history(employee)
        else:
            job_history.end = self.get_job_end_date()
            job_history.save()

    def get_job_start_date(self):
        return self.employee_data['job_history']['start_date']

    def get_job_end_date(self):
        end_date = self.employee_data['job_history']['end_date']
        return end_date if end_date else None

    def create_org_history(self, employee):

        try:
            headquater = Headquater.objects.get(code=self.employee_data['org_history']['head_code'])
            organization = Organization.objects.get(code=self.employee_data['org_history']['org_code'], headquater=headquater)
            OrgHistory.objects.create(agency_employee=employee,
                                      headquater=headquater,
                                      organization=organization,
                                      number=self.get_org_history_number(),
                                      start=self.get_org_history_start_date(),
                                      end=self.get_org_history_end_date())
        except Headquater.DoesNotExist:
            pass

    def update_or_create_org_history(self, employee):
        headquater = Headquater.objects.get(code=self.employee_data['org_history']['head_code'])
        organization = Organization.objects.get(code=self.employee_data['org_history']['org_code'], headquater=headquater)

        org_history = OrgHistory.objects.filter(agency_employee_id=employee.id, organization_id=organization.id,
                                                end=self.get_org_history_end_date()).first()
        if org_history is None:
            self.create_org_history(employee)
        else:
            org_history.start = self.get_org_history_start_date()
            org_history.number = self.get_org_history_number()
            org_history.save()

    def get_org_history_number(self):
        return self.employee_data['org_history']['number']

    def get_org_history_start_date(self):
        return self.employee_data['org_history']['start_date'] or self.employee_data['receipt_date']

    def get_org_history_end_date(self):
        return self.employee_data['org_history']['end_date'] or None

    def create_doc(self, employee):
        doc_type = DocType.objects.get(code=self.employee_data['doc']['doc_code'])
        EmployeeDoc.objects.create(agency_employee_id=employee.id,
                                   doc_type_id=doc_type.id,
                                   start=self.get_doc_start_date(),
                                   end=self.get_doc_end_date(),
                                   comments=self.employee_data['doc']['comments'])

    def update_or_create_doc(self, employee):
        doc_type = DocType.objects.get(code=self.employee_data['doc']['doc_code'])

        doc = EmployeeDoc.objects.filter(agency_employee_id=employee.id, doc_type_id=doc_type.id,
                                         start=self.get_doc_start_date()).first()
        if doc is None:
            self.create_doc(employee)
        else:
            doc.end = self.get_doc_end_date()
            doc.comments = self.employee_data['doc']['comments']
            doc.save()

    def get_doc_start_date(self):
        return self.employee_data['doc']['start_date']

    def get_doc_end_date(self):
        end_date = self.employee_data['doc']['end_date']
        return end_date if end_date else None
