import json
import re

from . import AppError, MultiplayerError, UserDisplayError
from .http import JsonError, JsonMultiplayerError, JsonUserDisplayError
from .utils import from_unix, month_end
from apps.lib.utils import send_sentry_exception
from apps.orgunits.models import Department, Organization, Workplace

from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View


class JsonView(View):
    """
    Обёртка для view, автоматически парсит тело запроса (если таковое есть)
    как JSON и передаёт его как второй парметр в соотв. метод.
    Ловит все ошибки типа `AppError` и возвращает их `message` как `JsonError(message)`.
    """

    def get_str_data(self, request):
        if request.body:
            return json_loads_or_error(request.body.decode('utf-8'))
        return None

    def dispatch(self, request, *args, **kwargs):
        handler = None
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), None)

        if handler is None:
            return self.http_method_not_allowed(request, *args, **kwargs)

        try:
            data = self.get_str_data(request)
            return handler(request, data, *args, **kwargs)

        except MultiplayerError as ex:
            return JsonMultiplayerError(ex.message)

        except UserDisplayError as ex:
            return JsonUserDisplayError(ex.message)

        except AppError as ex:
            send_sentry_exception()
            return JsonError(ex.message)

        except Exception as ex:
            send_sentry_exception()
            raise


def json_loads_or_error(text, msg='json parsing error'):
    try:
        return json.loads(text)
    except ValueError as e:
        raise AppError(msg+': '+e.args[0])


def get_object_or_error(model_class, **kwargs):
    msg = kwargs.pop('msg_', "'%s' not found by %s" % (model_class.__name__, kwargs))
    try:
        return model_class.objects.get(**kwargs)
    except model_class.DoesNotExist as e:
        raise AppError(msg) from e


def get_or_error(dict_, attr_name, msg=None):
    if attr_name in dict_:
        return dict_[attr_name]
    else:
        if msg is None:
            msg = 'missing "'+attr_name+'" attribute'
        raise AppError(msg)


def get_int_or_error(dict_, attr_name, msg=None):
    value = get_or_error(dict_, attr_name, msg)
    error_unless_int(value, msg or ('attribute "'+attr_name+'" is not int'))
    return value


def get_list_or_error(dict_, attr_name, msg=None):
    value = get_or_error(dict_, attr_name, msg)
    error_unless_list(value, msg or ('attribute "'+attr_name+'" is not list'))
    return value


def get_dict_or_error(dict_, attr_name, msg=None):
    value = get_or_error(dict_, attr_name, msg)
    error_unless_dict(value, msg or ('attribute "'+attr_name+'" is not dict'))
    return value


def error_unless_int(val, msg='not int'):
    if not isinstance(val, int):
        raise AppError(msg)


def error_unless_list(val, msg='not list'):
    if not isinstance(val, list):
        raise AppError(msg)


def error_unless_dict(val, msg='not dict'):
    if not isinstance(val, dict):
        raise AppError(msg)


def error_unless_employee_authorised(user):
    if not user.is_authenticated:
        raise AppError({'name': 'not_authorized'})
    try:
        return user.employee
    except ObjectDoesNotExist:
        raise AppError({'name': 'not_authorized'})


def with_start_end_dtimes(func):
    """
    Декоратор, конвертирует два строковых таймстампа (start/end_dtime)
    в datetime, проверяет ошибки.
    """
    def wrapped(request, **kwargs):
        try:
            start_dtime = from_unix(int(request.GET['start_dtime']))
            end_dtime = from_unix(int(request.GET['end_dtime']))
        except KeyError as e:
            return JsonError("missing %s parameter" % e.args[0])
        except ValueError as e:
            return JsonError('wrong timestamp in interval: '+e.args[0])

        if (end_dtime - start_dtime).days > 6*7:
            return JsonError('can not return more than 6 weeks')

        kwargs['start_dtime'] = start_dtime
        kwargs['end_dtime'] = end_dtime
        return func(request, **kwargs)
    return wrapped


def with_start_end_dates(func):
    """
    Декоратор, конвертирует две строковые даты (start/end_date)
    в date, проверяет ошибки.
    """
    def wrapped(request, **kwargs):
        try:
            start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d').date()
        except KeyError as e:
            return JsonError("missing %s parameter" % e.args[0])
        except ValueError as e:
            return JsonError('wrong date in interval: '+e.args[0])

        if (end_date - start_date).days > 6*7:
            return JsonError('can not return more than 6 weeks')

        kwargs['start_date'] = start_date
        kwargs['end_date'] = end_date
        return func(request, **kwargs)
    return wrapped


def with_month_date(func):
    """
    Декоратор, конвертирует параметр month=2015-08
    в аргументы month_start_date и month_end_date, проверяет ошибки.
    """
    def wrapped(request, **kwargs):
        try:
            start_date = datetime.strptime(request.GET['month'], '%Y-%m').date()
        except KeyError as e:
            return JsonError('missing %s parameter' % e.args[0])
        except ValueError as e:
            return JsonError('wrong month: ' + e.args[0])

        end_date = month_end(start_date)

        kwargs['month_start_date'] = start_date
        kwargs['month_end_date'] = end_date
        return func(request, **kwargs)
    return wrapped


def with_orgunit_filter(*orgunits_kinds):
    """
    Декоратор, находит по `orgunit_key` (типа "department#12")
    орг.единицу в базе и отправяет её в параметр `orgunit`.
    """
    for kind in orgunits_kinds:
        if kind not in ['workplace', 'department', 'organization']:
            raise ValueError("wrong orgunit kind '%s'" % kind)

    regexp_str = r'^(%s)#(\d+)$' % '|'.join(orgunits_kinds)
    regexp = re.compile(regexp_str)
    orgunit_classes = {'workplace': Workplace, 'department': Department, 'organization': Organization}

    def decorator(func):
        def wrapped(request, **kwargs):
            try:
                key = request.GET['orgunit_key']
            except KeyError:
                return JsonError("missing 'orgunit_key' parameter")

            m = regexp.match(key)
            if m is None:
                return JsonError("expected 'orgunit_key' to be like '<%s>#<id>', got '%s'"
                                 % ('|'.join(orgunits_kinds), key))

            kind, pk = m.groups()
            try:
                kwargs['orgunit'] = get_object_or_error(orgunit_classes[kind], pk=int(pk))
            except AppError as ex:
                return JsonError(ex.message)
            return func(request, **kwargs)
        return wrapped
    return decorator


def with_orgunits_filter(*orgunits_kinds):
    """
    Декоратор, вынимает из параметров массивы айдишников орг.единиц
    (типа department_ids=[1,2,3]) и отправляет их в соотв. параметры вьюхи.
    """
    for kind in orgunits_kinds:
        if kind not in ['workplace', 'department', 'organization']:
            raise ValueError("wrong orgunit kind '%s'" % kind)
    required_params = [k+'_ids' for k in orgunits_kinds]

    def decorator(func):
        def wrapped(request, **kwargs):
            for param in required_params:
                try:
                    kwargs[param] = json.loads(request.GET[param])
                except KeyError:
                    return JsonError("missing '%s' parameter" % param)
                except ValueError:
                    return JsonError("error parsing '%s' as json array" % param)
                for i in kwargs[param]:
                    if not isinstance(i, int):
                        return JsonError("parameter '%s' is not a json INT array: %s" % (param, kwargs[param]))
            return func(request, **kwargs)
        return wrapped
    return decorator


def with_compact_int_list(param, separator='_'):
    """
    Декоратор, вынимает из параметров массив айдишников
    (типа employee_ids=1_2_3) и отправляет их в соотв. параметры вьюхи.
    """
    def decorator(func):
        def wrapped(request, **kwargs):
            try:
                raw_value = request.GET[param].strip()
            except KeyError:
                return JsonError("missing '%s' parameter" % param)
            kwargs[param] = [] if raw_value == '' else raw_value.split(separator)
            try:
                kwargs[param] = [int(i) for i in kwargs[param]]
            except ValueError:
                return JsonError(f"parameter '{param}' is not a '{separator}'-separated int array: {raw_value}")
            return func(request, **kwargs)
        return wrapped
    return decorator


def with_string_list(param):
    """
    Декоратор, вынимает из параметров массив строк и отправляет его в соотв. параметр вьюхи.
    """
    def decorator(func):
        def wrapped(request, **kwargs):
            try:
                value = json.loads(request.GET[param])
            except KeyError:
                return JsonError(f"missing '{param}' parameter")
            except ValueError:
                return JsonError(f"parameter '{param}' is not a json: {request.GET[param]}")
            if not isinstance(value, list):
                return JsonError(f"parameter '{param}' is not a json array: {request.GET[param]}")
            for item in value:
                if not isinstance(item, str):
                    return JsonError(f"parameter '{param}' is not a json string array: {request.GET[param]}")
            kwargs[param] = value
            return func(request, **kwargs)
        return wrapped
    return decorator
