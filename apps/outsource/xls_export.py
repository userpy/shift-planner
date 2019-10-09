"""
Copyright 2018 ООО «Верме»

Классы для экспорта моделей в xls
"""

from collections import OrderedDict
import io

import xlwt


class OrgLinkXLSExporter:
    cols = OrderedDict([
        ('headquater', 'Код клиента'),
        ('organization', 'Код организации'),
        ('aheadquarter', 'Код компании-промоутера'),
        ('agency', 'Код подразделения промоутера'),
    ])

    def __init__(self):
        self.header_style = xlwt.easyxf('font: bold on')
        self.wb = None
        self.ws = None

    def generate(self, orglinks):
        file = io.BytesIO()
        self.wb = xlwt.Workbook(encoding='urf-8', style_compression=2)
        self.ws = self.wb.add_sheet('orglinks', cell_overwrite_ok=False)
        for rownum, row in enumerate(self.get_rows(orglinks)):
            self.write_row(rownum, row)
        self.wb.save(file)
        file.seek(0)
        return file

    def write_row(self, rownum, row):
        for colnum, name in enumerate(self.cols.keys()):
            value = row.get(name)
            style = xlwt.Style.default_style
            if rownum == 0:
                style = self.header_style
            self.ws.write(rownum, colnum, value, style)

    def get_rows(self, orglinks):
        yield self.get_caption_row()
        for orglink in orglinks:
            yield from self.get_orglink_rows(orglink)

    def get_caption_row(self):
        row = {}
        for name, label in self.cols.items():
            row[name] = label
        return row

    def get_orglink_rows(self, orglink):
        row = {}
        for attr in self.cols.keys():
            row[attr] = getattr(orglink, attr).code
        yield row
