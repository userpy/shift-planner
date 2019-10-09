from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from wfm.settings import DEBUG
import json


class JsonResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        indent = "\t" if DEBUG else None
        data = json.dumps(data, cls=DjangoJSONEncoder, indent=indent, ensure_ascii=False)
        kwargs.setdefault('content_type', 'application/json')
        super().__init__(content=data, **kwargs)


def JsonOk(**kwargs):
    kwargs['result'] = 'ok'
    return JsonResponse(kwargs)


def JsonError(msg, **kwargs):
    kwargs['result'] = 'error'
    kwargs['error'] = msg
    return JsonResponse(kwargs)


def JsonMultiplayerError(msg):
    res = {'result': 'multiplayer-error', 'error': msg}
    return JsonResponse(res)


def JsonUserDisplayError(msg):
    res = {'result': 'user-error', 'error': msg}
    return JsonResponse(res)

def JsonUserDisplayErrorExt(status, name, message=None, long_description=None):
    """
    Версия JsonUserDisplayError с фиксированным набором полей.
        name - текстовый код ошибки (типа 'book_shift:shift_not_found')
        message - готовое текстовое сообщение
        long_description - длинное сообщение об ошибке, которое (скорее всего) будет скрыто под спойлером
    """
    data = {'name': name}
    if message is not None:
        data['message'] = message
    if long_description is not None:
        data['long_description'] = long_description
    return JsonResponse({'result': 'user-error', 'error': data}, status=status)
