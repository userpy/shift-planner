"""
Copyright 2018 ООО «Верме»

Парсеры модуля outsourcing
"""

from collections import defaultdict

import xlrd
from django.db import transaction

from .models import Agency, Headquater, Organization, OrgLink


class XLSParser:
    """
    Парсер xls-файла для импорта связей между организациями и агентствами
    """

    def __init__(self):
        self.record_data = {}
        self.processed_records = set()
        self.created_records_data = defaultdict(list)

    def parse(self, file_contents):
        workbook = xlrd.open_workbook(file_contents=file_contents)
        sheet = workbook.sheet_by_index(0)
        errors = []
        for rownum in range(1, sheet.nrows):
            row = sheet.row_values(rownum)
            try:
                self.record_data = self.get_struct_from_row(row, workbook)
                self.process_record_data()
            except Exception as e:
                errors.append({'rownum': rownum, 'exc': e})

        return errors

    def process_record_data(self):
        """
        Override this method for custom parser
        :return:
        """
        return NotImplementedError

    @staticmethod
    def clean_value(value):
        if isinstance(value, (bytes, str)):
            if value:
                if isinstance(value, bytes):
                    value = value.encode('utf-8')
                value = value.strip().replace("'", '')
            else:
                value = ''
        return value

    @staticmethod
    def get_struct_from_row(row, workbook):
        """
        Override this method for custom parser
        :param row: sequence of xlrd.sheet.Cell
        :param workbook: needed for dates
        :return:
        """
        return NotImplementedError


class OrgLinkXLSParser(XLSParser):

    def process_record_data(self):
        with transaction.atomic():
            try:
                # If no exception, do nothing
                OrgLink.objects.get(
                    organization__code=self.record_data['organization_code'],
                    agency__code=self.record_data['agency_code'],
                )
            except OrgLink.DoesNotExist:
                try:
                    headquarter = Organization.objects.get(code=self.record_data['organization_code']).headquater
                    organization = Organization.objects.get(code=self.record_data['organization_code'])
                except Organization.MultipleObjectsReturned:
                    headquarter = Headquater.objects.get(code=self.record_data['headquarter_code'])
                    organization = Organization.objects.get(headquater=headquarter,
                                                            code=self.record_data['organization_code'])

                try:
                    aheadquarter = Agency.objects.get(code=self.record_data['agency_code']).headquater
                    agency = Agency.objects.get(code=self.record_data['agency_code'])
                except Agency.MultipleObjectsReturned:
                    aheadquarter = Headquater.objects.get(code=self.record_data['aheadquarter_code'])
                    agency = Agency.objects.get(headquater=aheadquarter, code=self.record_data['agency_code'])

                OrgLink.objects.create(headquater=headquarter,
                                       organization=organization,
                                       aheadquarter=aheadquarter,
                                       agency=agency)

    @staticmethod
    def get_struct_from_row(row, workbook):
        return {
            'headquarter_code': XLSParser.clean_value(row[0]),
            'organization_code': XLSParser.clean_value(row[1]),
            'aheadquarter_code': XLSParser.clean_value(row[2]),
            'agency_code': XLSParser.clean_value(row[3]),
        }
