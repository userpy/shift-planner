#
# Copyright 2018 ООО «Верме»
#
# Файл пересчета объектов QuotaInfo
#

# coding=utf-8;

from django.core.management.base import BaseCommand
from apps.outsource.models import Quota, QuotaInfo
from apps.outsource.methods import get_quota_related_shifts
from apps.shifts.models import PromoShift
from django.db.models import Q
import datetime
import calendar


class Command(BaseCommand):
    help = 'Recalcs QuotaInfo'

    def add_arguments(self, parser):
        parser.add_argument('--month', type=str, help='месяц', default='')

    def handle(self, *args, **options):
        month = options.get('month')
        # Если задан месяц
        if month:
            month_start = datetime.datetime.strptime(month, '%d.%m.%Y').date()
            month_max_day = calendar.monthrange(month_start.year, month_start.month)[1]
            month_end = month_start.replace(day=month_max_day)

        # Получаем квоты
        quotas = Quota.objects.all()
        if month:
            quotas = quotas.filter(Q(start__lte=month_start, end__gte=month_end) |
                                   Q(start__lte=month_start, end__isnull=True))

        # Получение смен по квотам
        for quota in quotas:
            affected_quota_infos = QuotaInfo.objects.filter(quota=quota, month=month_start)
            PromoShift.objects.filter(quota_info__in=affected_quota_infos).update(quota_info=None)
            affected_quota_infos.delete()

            quota_related_shifts = get_quota_related_shifts(quota).filter(start_date__gte=month_start,
                                                                          start_date__lte=month_end)
            if not quota_related_shifts.exists():
                continue

            for quota_number in range(0, quota.value_total):
                number_shifts = quota_related_shifts.filter(quota_number=quota_number)
                number_total = number_shifts.count()
                number_open = number_shifts.filter(agency_employee__isnull=True).count()
                quota_info = QuotaInfo.objects.create(month=month_start,
                                                      quota=quota,
                                                      quota_number=quota_number,
                                                      shifts_count=number_total,
                                                      open_shifts_count=number_open)
                number_shifts.update(quota_info=quota_info)
        print('QuotaInfo created for all PromoShifts')
