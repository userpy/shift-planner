"""
Copyright 2018 ООО «Верме»

Класс для экспорта записей модели PromoShifts в xls
"""

import io
import xlwt

from collections import OrderedDict
from datetime import date


class PromoShiftsXLSExporter:
    cols = OrderedDict([
        ('state', 'Состояние'),
        ('agency__code', 'Подразделение промоутера (ИД)'),
        ('agency__name', 'Подразделение промоутера (имя)'),
        ('aheadquarter__code', 'Компания промоутер (ИД)'),
        ('aheadquarter__name', 'Компания промоутер (имя)'),
        ('organization__code', 'Магазин (ИД)'),
        ('organization__name', 'Магазин (имя)'),
        ('store_area__code', 'Зона магазина'),
        ('start_date', 'Дата начала смены'),
        ('start', 'Время начала смены'),
        ('end_date', 'Дата окончания смены'),
        ('end', 'Время окончания смены'),
        ('duration', 'Продолжительность'),
        ('employee_extnumber', 'Сотрудник (ИД)'),
        ('employee_fullname', 'Сотрудник (имя)'),
    ])

    def __init__(self):
        self.date_style = xlwt.XFStyle()
        self.date_style.num_format_str = 'DD.MM.YYYY'
        self.header_style = xlwt.easyxf('font: bold on')

    def generate(self, employees):
        file = io.BytesIO()
        self.wb = xlwt.Workbook(encoding='utf-8', style_compression=2)
        self.ws = self.wb.add_sheet('promoshifts', cell_overwrite_ok=False)
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

    def get_rows(self, promoshifts):
        yield self.get_caption_row()
        for promoshift in promoshifts:
            yield from self.get_promoshift_rows(promoshift)

    def get_caption_row(self):
        row = {}
        for col_num, (name, label) in enumerate(self.cols.items()):
            if isinstance(name, str):
                row[name] = label
            elif isinstance(name, tuple):
                row.setdefault(name[0], {})
                row[name[0]][name[1]] = label
        return row

    def get_promoshift_rows(self, promoshift):
        row = {}
        for attr in [
            'state',
            'agency__code',
            'agency__name',
            'aheadquarter__code',
            'aheadquarter__name',
            'organization__code',
            'organization__name',
            'store_area__code',
            'start_date',
            'start',
            'end_date',
            'end',
            'duration',
            'employee_extnumber',
            'employee_fullname'
        ]:
            asplit = attr.split('__')
            if len(asplit) == 2:
                row[attr] = getattr(getattr(promoshift, asplit[0]), asplit[1])
            elif attr == 'start' or attr == 'end':
                row[attr] = getattr(promoshift, attr).strftime("%H:%M")
            elif attr == 'end_date':
                row[attr] = getattr(promoshift, 'end').date()
            elif attr == 'employee_extnumber':
                extnumber = ''
                employee = getattr(promoshift, 'agency_employee')
                if employee:
                    headquarter = getattr(promoshift, 'headquarter')
                    start = getattr(promoshift, 'start')
                    extnumber = employee.get_number_in_organization(headquarter, start)
                row[attr] = extnumber
            elif attr == 'employee_fullname':
                employee = getattr(promoshift, 'agency_employee')
                if employee:
                    employee = employee.name
                row[attr] = employee
            else:
                row[attr] = getattr(promoshift, attr)
        yield row