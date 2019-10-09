from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_weekday(value):
    if value < 1 or value > 7:
        raise ValidationError(_('weekday number "%(value)s" is outside [1, 7]'), params={'value': value})


def validate_minutes(value):
    if value % 15 != 0:
        raise ValidationError(_('minutes "%(value)s" are not multiple of 15'), params={'value': value})


def validate_month_number(value):
    if value < 1 or value > 12:
        raise ValidationError(_('month number "%(value)s" is outside [1, 12]'), params={'value': value})


def validate_dtime_15m(value):
    if value.minute % 15 != 0 or value.second != 0 or value.microsecond != 0:
        raise ValidationError('время "%(value)s" не кратно 15 минутам', params={'value': value})
