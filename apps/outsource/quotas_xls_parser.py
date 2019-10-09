import datetime
import xlrd

from django.db import transaction
from django.db.models import Q

from apps.outsource.models import Headquater, Organization, Quota, StoreArea
from collections import defaultdict

from .methods import *

def name_or_code_q(name_or_code):
    return Q(name=name_or_code) | Q(code=name_or_code)


class QuotasXLSParser:
    """
    Парсер xls-файла со списком квот, импортируемых в разделе клиента
    """

    def __init__(self):
        self.quota_data = {}
        self.processed_quotas = set()
        self.created_quota_data = defaultdict(list)

    def parse(self, file_contents):
        rb = xlrd.open_workbook(file_contents=file_contents)
        sheet = rb.sheet_by_index(0)
        errors = []
        for rownum in range(1, sheet.nrows):
            row = sheet.row_values(rownum)
            try:
                self.quota_data = self.get_struct_from_row(row, rb)
                self.process_quota_data()
            except Exception as exc:
                errors.append({'rownum': rownum, 'exc': exc})
        return errors

    def process_quota_data(self):
        # TODO - Переделать на сериалайзер, не ясно, зачем мы для импорта пишем отдельный код
        with transaction.atomic():
            try:
                quota = Quota.objects.get(store__code=self.quota_data['store'],
                                          area__code=self.quota_data['area'],
                                          promo__code=self.quota_data['promo']
                                          )
                self.update_quota(quota)
            except Quota.DoesNotExist:
                quota = self.create_quota()
                self.created_quota_data[quota].append(self.quota_data)
            except Exception:
                raise
        self.processed_quotas.add(quota)

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
            'store': get_int_as_string(clean_value(row[0])),
            'area': get_int_as_string(clean_value(row[2])),
            'promo': get_int_as_string(clean_value(row[3])),
            'quota_type': clean_value(row[5]),
            'value': get_int_as_string((row[6])),
        }

    def create_quota(self):
        promo = Headquater.objects.get(code=self.quota_data['promo'], party='promo')
        store = Organization.objects.get(code=self.quota_data['store'])
        area = StoreArea.objects.get(code=self.quota_data['area'])

        quota = Quota()
        quota.promo = promo
        quota.store = store
        quota.area = area
        quota.quota_type = self.quota_data['quota_type']
        quota.value = self.quota_data['value']
        quota.save()

        return quota

    def update_quota(self, quota):
        set_quota_value(quota, self.quota_data['value'])