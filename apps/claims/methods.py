from django.db.models import Q
from django.utils import timezone
from datetime import datetime
import calendar

from .models import ClaimRequest


def make_claims_queryset(unit_headquarter=None, unit=None, date=None, period_start=None, period_end=None):
    """Формирование queryset смен"""
    start = None
    end = None

    if period_start and period_end:
        start = datetime.strptime(period_start, '%Y-%m-%d')
        end = datetime.strptime(period_end, '%Y-%m-%d')
        end = datetime(year=end.year,
                       month=end.month,
                       day=end.day,
                       hour=23,
                       minute=59,
                       second=59,
                       microsecond=999999)

    if date:
        if isinstance(date, str):
            start = datetime.strptime(date, '%Y-%m-%d')
        else:
            start = datetime.combine(date, datetime.min.time())
        end = datetime(year=start.year,
                       month=start.month,
                       day=list(calendar.monthrange(start.year, start.month))[1],
                       hour=23,
                       minute=59,
                       second=59,
                       microsecond=999999)

    """Ограничиваем по клиенту и орг. единице"""
    if unit_headquarter.party in ['agency', 'promo']:
        claims_query_set = ClaimRequest.objects.filter(agency__headquater=unit_headquarter)
        if unit:
            claims_query_set = claims_query_set.filter(agency=unit)
    else:
        claims_query_set = ClaimRequest.objects.filter(headquater=unit_headquarter)
        if unit:
            claims_query_set = claims_query_set.filter(Q(organization=unit) | Q(organization__parent=unit))

    if start and end:
        claims_query_set = claims_query_set.filter(dt_created__gte=start, dt_created__lte=end)

    return claims_query_set
