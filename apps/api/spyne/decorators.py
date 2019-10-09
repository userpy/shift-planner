#
# Copyright 2018 ООО «Верме»
#
# Файл декораторов для Spyne
# Используется для проверки прав доступа в методах и логгирования
#

import json
import logging
import time

from decorator import decorator

from django.db import transaction

from spyne.protocol.dictdoc import SimpleDictDocument
from spyne.protocol.json import JsonDocument
from spyne.protocol.soap import Soap11

from .faults import AuthenticationError
from .helpers import AttrDict, json_value_converter

from apps.employees.models import EmployeeEvent
from apps.permission.methods import get_available_clients_by_user

logger = logging.getLogger('api')


@decorator
def soap_logger(func, *args, **kwargs):
    time_start = time.time()
    error = None
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error = e
        raise e
    finally:
        # Продолжительность
        duration = time.time() - time_start

        simple_dict = SimpleDictDocument()

        header = simple_dict.object_to_simple_dict(
            type(args[0].in_header), args[0].in_header)
        body = json.dumps(
            args[0].in_object.as_dict(), default=json_value_converter)
        body = json.loads(body)

        tags = None
        headquater = None
        login = None

        if 'login' in header:
            login = header['login']
        elif '' in header and 'login' in header['']:
            login = header['']['login']

        if login:
            headquater = get_available_clients_by_user(username=login)[0] #first()

        if 'employeeevent' in body and 'guid' in body['employeeevent']:
            try:
                event = EmployeeEvent.objects.get(guid=body['employeeevent']['guid'])
                headquater = {'id': event.headquater.id, 'name': event.headquater.name}
                tags = ['organization#'+str(event.organization_id), 'employee#'+str(event.agency_employee_id)]
            except EmployeeEvent.DoesNotExist:
                pass

        level = 'INFO'
        msg = 'Время выполнения: {0}\n'
        if error:
            level = 'ERROR'
            msg += 'Ошибка: {1}'
        if isinstance(args[0].in_protocol, JsonDocument):
            source = 'REST API'
        elif isinstance(args[0].in_protocol, Soap11):
            source = 'SOAP API'
        else:
            source = 'undefined API'

        message = msg.format(round(duration, 1), error)

        if tags:
            message += 'Теги: ' + ','.join(tags)

        extra = {'source': source,
                 'method': func.__name__,
                 'duration': duration,
                 'headquater': headquater.get('name', '--'),
                 'params': {
                     'header': header,
                     'body': body,
                 }
                 }
        if level == 'INFO':
            logger.info(message, extra=extra)
        elif level == 'ERROR':
            logger.error(message, extra=extra)


@decorator
def check_auth_data(func, *args, **kwargs):
    """
    Check auth data in header.

    If header is None trying get the data from body.
    """
    in_document = args[0].in_document
    if args[0].in_header is None:
        try:
            auth_data = in_document[func.__name__]['authData']
        except KeyError:
            raise AuthenticationError(None)

        args[0].in_header = AttrDict()
        args[0].in_header.login = auth_data.get('login')
        args[0].in_header.password = auth_data.get('password')

    return func(*args, **kwargs)
