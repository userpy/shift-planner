"""
Copyright 2018 ООО «Верме»

Класс для экспорта записей модели Employee в xls
"""

import io
import xlwt

from collections import OrderedDict
from datetime import date


class EmployeesXLSExporter:
    cols = OrderedDict([
        ('number', 'ТН'),
        ('surname', 'Фамилия'),
        ('firstname', 'Имя'),
        ('patronymic', 'Отчество'),
        ('gender', 'Пол'),
        ('date_of_birth', 'Дата рождения'),
        ('place_of_birth', 'Место рождения'),
        ('agency', 'Агентство'),
        ('receipt', 'Дата приема'),
        ('dismissal', 'Дата увольнения'),

        (('org_history', 'head_code'),  'Клиент'),
        (('org_history', 'org_code'),   'Город'),
        (('org_history', 'number'),     'ТН в организации'),
        (('org_history', 'start_date'), 'Работает с'),
        (('org_history', 'end_date'),   'Работает до'),

        (('job_history', 'job_code'),   'Должность'),
        (('job_history', 'start_date'), 'Действует с'),
        (('job_history', 'end_date'),   'Действует до'),

        (('doc', 'doc_code'),   'Тип документа'),
        (('doc', 'start_date'), 'Действует с'),
        (('doc', 'end_date'),   'Действует до'),
        (('doc', 'comments'),   'Комментарий'),

    ])

    def __init__(self):
        self.date_style = xlwt.XFStyle()
        self.date_style.num_format_str = 'DD.MM.YYYY'
        self.header_style = xlwt.easyxf('font: bold on')

    def generate(self, employees):
        file = io.BytesIO()
        self.wb = xlwt.Workbook(encoding='utf-8', style_compression=2)
        self.ws = self.wb.add_sheet('employees', cell_overwrite_ok=False)
        for row_num, row in enumerate(self.get_rows(employees)):
            self.write_row(row_num, row)
        self.wb.save(file)
        file.seek(0)
        return file

    def write_row(self, row_num, row):
        for col_num, name in enumerate(self.cols.keys()):
            if isinstance(name, str):
                value = row.get(name)
            elif isinstance(name, tuple):
                value = row.get(name[0])
                if value is not None:
                    value = value.get(name[1])
            style = xlwt.Style.default_style
            if row_num == 0:
                style = self.header_style
            elif isinstance(value, date):
                style = self.date_style
            self.ws.write(row_num, col_num, value, style)

    def get_rows(self, employees):
        yield self.get_caption_row()
        for employee in employees:
            yield from self.get_employee_rows(employee)

    def get_caption_row(self):
        row = {}
        for col_num, (name, label) in enumerate(self.cols.items()):
            if isinstance(name, str):
                row[name] = label
            elif isinstance(name, tuple):
                row.setdefault(name[0], {})
                row[name[0]][name[1]] = label
        return row

    def get_employee_rows(self, employee):
        org_histories = list(employee.orghistory_set.order_by('start', '-end'))
        job_histories = list(employee.jobhistory_set.order_by('start', '-end'))
        docs = list(employee.employeedoc_set.order_by('id'))

        rows_count = max(1, len(org_histories), len(job_histories), len(docs))

        job_histories += [None] * (rows_count - len(job_histories))
        org_histories += [None] * (rows_count - len(org_histories))
        docs += [None] * (rows_count - len(docs))
        histories = zip(org_histories, job_histories, docs)

        # генерим одну-несколько строк по данным текущего сотрудника
        for i, (org_history, job_history, doc) in enumerate(histories):
            row = {}
            if i == 0:  # основные параметры сотрудниа пишем только в первую строку
                for attr in ['agency', 'number', 'surname', 'firstname', 'patronymic', 'gender', 'date_of_birth', 'place_of_birth', 'receipt', 'dismissal']:
                    row[attr] = getattr(employee, attr)
                    if attr == 'agency':
                        row[attr] = row[attr].code
            else:  # в остальные строки пишем только номер
                row['number'] = employee.number
                row['agency'] = employee.agency.code

            if org_history is not None:
                row['org_history'] = {
                    'head_code': org_history.headquater.code,
                    'org_code': org_history.organization.code,
                    'number': org_history.number,
                    'start_date': org_history.start,
                    'end_date': org_history.end,
                }

            if job_history is not None:
                row['job_history'] = {
                    'job_code': job_history.job.code,
                    'start_date': job_history.start,
                    'end_date': job_history.end,
                }

            if doc is not None:
                row['doc'] = {
                    'doc_code': doc.doc_type.code,
                    'start_date': doc.start,
                    'end_date': doc.end,
                    'comments': doc.comments,
                }

            yield row
