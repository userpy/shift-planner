#
# Copyright 2018 ООО «Верме»
#
# Файл описания вспомогательных функций для Spyne
#

import datetime
import logging
import uuid

from spyne.protocol.dictdoc import SimpleDictDocument

from .faults import AuthenticationError, AuthorizationError, CustomError
from django.contrib.auth import authenticate
from apps.permission.methods import check_unit_permission_by_user
from apps.outsource.models import Headquater

logger = logging.getLogger('api')


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def json_value_converter(value):
    simple_dict = SimpleDictDocument()
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    elif isinstance(value, uuid.UUID):
        return (str(value))
    elif hasattr(value, 'Value'):
        return simple_dict.object_to_simple_dict(
            type(value), value)


def auth_and_check_perms(login, password):
    user = authenticate(username=login, password=password)
    if not user:
        raise AuthenticationError(login)

    if user.is_superuser:
        return
    else:
        raise CustomError('No access')


def auth_and_check_unit_perms(login, password, unit, action):
    user = authenticate(username=login, password=password)
    if not user:
        raise AuthenticationError(login)

    if check_unit_permission_by_user(user, unit, action):
        return
    else:
        raise CustomError('No permission')


def get_headquater_id(headquater_code):
    headquater = Headquater.objects.filter(code=headquater_code).first()
    if headquater:
        return headquater.id
    else:
        raise CustomError(f'Headquater {headquater_code} is not registered')
