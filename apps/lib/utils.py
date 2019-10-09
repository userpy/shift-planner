import base64
import fcntl
import functools
import glob
import json
import os
import phonenumbers
import shutil
import contextlib

from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.db.utils import ProgrammingError
from django.utils.timezone import get_current_timezone, now

from raven import Client


def unix(dtime):
    return dtime and int(dtime.timestamp())


def from_unix(stamp):
    if stamp is None:
        return None
    return datetime.fromtimestamp(stamp, timezone.utc)


def is_midnight(dtime):
    return dtime.hour + dtime.minute + dtime.second + dtime.microsecond == 0


def month_start(date_):
    return date(date_.year, date_.month, 1)


def month_end(date_):
    next_month_date = date(date_.year, date_.month, 28) + timedelta(days=4)
    return next_month_date - timedelta(days=next_month_date.day)


def month_interval_from_middle(start_date, end_date):
    start = month_start(start_date + (end_date - start_date)/2)
    end = month_end(start)
    return start, end


def week_start(date_):
    if isinstance(date_, datetime):
        date_ = date_.date()
    return date_ - timedelta(days=date_.weekday())


def week_end(date_):
    if isinstance(date_, datetime):
        date_ = date_.date()
    return date_ + timedelta(days=6-date_.weekday())


def day_start(dtime):
    return dtime.replace(hour=0, minute=0, second=0, microsecond=0)


def daysrange(start_date, end_date, step=timedelta(1), include_last=False, warn_if_not_midnight=True):
    if isinstance(start_date, datetime):
        if warn_if_not_midnight and not is_midnight(start_date):
            print('warn: start_dtime of daysrange() is not midnight:', start_date)
        start_date = start_date.date()
    if isinstance(end_date, datetime):
        if warn_if_not_midnight and not is_midnight(end_date):
            print('warn: end_dtime of daysrange() is not midnight:', end_date)
        end_date = end_date.date()

    if include_last:
        end_date += timedelta(days=1)

    i = 0
    while True:
        cur_date = start_date + step*i
        if cur_date >= end_date:
            break
        yield cur_date
        i += 1


def months_delta(start_date, end_date):
    """ Возвращает количество полных месяцев между двумя датами """
    delta = (end_date.year - start_date.year)*12 + (end_date.month - start_date.month)
    if start_date.day > end_date.day:
        delta -= 1
    return delta


def content_type_ids_for_models(*models):
    types = ContentType.objects.get_for_models(*models)
    return [types[model].pk for model in models]


def send_sentry_message(message, **kwargs):
    sentry_dsn = settings.RAVEN_CONFIG.get('dsn', '')
    if sentry_dsn.strip():
        client = Client(sentry_dsn)
        client.captureMessage(message, **kwargs)


def send_sentry_exception():
    sentry_dsn = settings.RAVEN_CONFIG.get('dsn', '')
    if sentry_dsn.strip():
        client = Client(sentry_dsn)
        client.captureException()


def dtimes_to_dates(*dtimes, astimezone=None, strict=True):
    dates = []
    for dtime in dtimes:
        if astimezone is not None:
            dtime = dtime.astimezone(astimezone)
        if strict and not is_midnight(dtime):
            raise ValueError('datetime is not midnight: %s' % dtime)
        dates.append(dtime.date())
    return dates


def _date_to_dtime(date_, tz, astimezone):
    dtime = tz.localize(datetime.combine(date_, time(0, 0)))
    if astimezone is not None:
        dtime = dtime.astimezone(astimezone)
    return dtime


def dates_to_dtimes(*dates, tz=None, astimezone=None):
    if tz is None:
        tz = get_current_timezone()
    dtimes = []
    for date_ in dates:
        dtimes.append(_date_to_dtime(date_, tz, astimezone))
    return dtimes


def dates_interval_to_dtime(start_date, end_date):
    start_dtime, end_dtime = dates_to_dtimes(start_date, end_date)
    if end_dtime is not None:
        end_dtime += timedelta(days=1)
    return start_dtime, end_dtime


def dates_interval_to_dtime_or_none(start_date, end_date):
    tz = get_current_timezone()
    start_dtime = _date_to_dtime(start_date, tz, None)
    end_dtime = None
    if end_date is not None:
        end_dtime = _date_to_dtime(end_date, tz, None) + timedelta(days=1)
    return start_dtime, end_dtime

def current_utc_offset():
    return int(-get_current_timezone().utcoffset(datetime.now()).total_seconds() * 1000)

def dtime_interval_to_dates(start_dtime, end_dtime):
    start_date, end_date = dtimes_to_dates(start_dtime, end_dtime, strict=False)
    if is_midnight(end_dtime):
        end_date -= timedelta(days=1)
    return start_date, end_date


def must_be_dates(*args):
    for arg in args:
        if type(arg) != date:
            raise TypeError('expected <date> argument, got <%s>' % type(arg).__name__)


def must_be_datetimes(*args, with_tz=True):
    for arg in args:
        if type(arg) != datetime:
            raise TypeError('expected <datetime> argument, got <%s>' % type(arg).__name__)
        if with_tz and arg.tzinfo is None:
            raise TypeError('expected <datetime> to have tzinfo but it is None')


class DefaultDictKey(defaultdict):
    """ Подобие defaultdict, только переданную функцию вызывает с аргументом-ключом.
        Например:
            users_by_id = DefaultDictKey(lambda pk: User.objects.get(pk=pk)) """
    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        else:
            res = self[key] = self.default_factory(key)
            return res


def enum(**enums):
    """ Create Enum like type.
        Example:
        COLOR = enum(black=0, red=1, green=2)
        COLOR.red (1)
        COLOR.black (0) """
    return type('Enum', (), enums)


def method_lru_cache(*lru_args, **lru_kwargs):
    """ Аналог lru_cache для методов.
        TODO: (weakref) тут self начинает ссылаться сам на себя, что осложняет работу сборщику мусора. """
    def decorator(func):
        @functools.wraps(func)
        def wrapped_func(self, *args, **kwargs):
            cached_method = functools.lru_cache(*lru_args, **lru_kwargs)(func)
            cached_method = cached_method.__get__(self, self.__class__)
            setattr(self, func.__name__, cached_method)
            return cached_method(*args, **kwargs)
        return wrapped_func
    return decorator


@contextlib.contextmanager
def commit_manually():
    """ Выполянет блок кода с отключенным autocommit'ом.
        Т.е. можно вызывать transaction.rollback()/transaction.commit() вручную.
        При эксепшене rollback делается автоматически.
        Пример:
            with commit_manually():
                User.objects.create()
                transaction.rollback()
                User.objects.create()
                transaction.commit() """
    transaction.set_autocommit(False)
    try:
        yield
    except:
        transaction.rollback()
        raise
    finally:
        try:
            transaction.set_autocommit(True)  # если остались какие-то незакомиченные данные...
        except ProgrammingError:
            transaction.rollback()  # ...откатываем их, ...
            transaction.set_autocommit(True)  # ...включаем автокоммит снова...
            raise  # ...и кидаем эту ошибку дальше (потому что надо было коммитить)


def add_basic_auth_header(request, login, password):
    auth_str = '%s:%s' % (login, password)
    encoded_auth = base64.b64encode(auth_str.encode('ascii'))
    request.add_header("Authorization", "Basic %s" % encoded_auth.decode('utf-8'))


def merge_json_files(files_path, output_file):
    """
    Merge several json files into one.
    Can be useful for fixtures, for example.
    """
    out_data = []
    for f in glob.glob("{0}/*.json".format(files_path)):
        with open(f, "r") as infile:
            data = json.load(infile)

            i = 0
            while i < len(data):
                out_data.append(data[i])
                i += 1

    with open(output_file, "w") as outfile:
        json.dump(out_data, outfile, indent=2)

    shutil.rmtree(files_path)


def reformat_phone_number(number_str):
    try:
        num = phonenumbers.parse(number_str, settings.PHONENUMBERS_REGION)
    except phonenumbers.phonenumberutil.NumberParseException as ex:
        raise ValueError("phone number '%s' in invalid" % number_str) from ex
    if not phonenumbers.is_valid_number(num):
        raise ValueError("phone number '%s' in invalid" % number_str)
    return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)


def content_type_ids_for_models(*models):
    types = ContentType.objects.get_for_models(*models)
    return [types[model].pk for model in models]


def content_type_Q_for_models(*models):
    if len(models) == 0:
        return Q(id__in=[])
    q = Q()
    for model in models:
        q = q | Q(app_label=model._meta.app_label, model=model._meta.model_name)
    return q


class PidLockManager:
    """
    Manager of PID files for commands.
    Takes any arguments which uses for a filename.
    Tries to lock a file.
    In case if the file is already locked raises an error.
    Unlocks and deletes a file when an object will be destroying and only if
    the file has been created by this instance.
    """

    def __init__(self, *args, **kwargs):
        file_name = ''
        if args:
            values = args
        elif kwargs:
            values = kwargs.keys()
        else:
            values = []

        # make a filename with arguments
        for i in range(len(values)):
            file_name += '_{0}_'.format(values[i])

        file_name = '_{0}_.pid'.format(file_name)
        path = '/tmp/pids/'
        os.makedirs(path, exist_ok=True)
        self.file_path = os.path.join(path, file_name)
        self.locked_file = None

    def __del__(self):
        self.close()

    def close(self):
        # delete a file only if it has been created by this instance
        if self.locked_file:
            self.locked_file.close()
            os.remove(self.file_path)

    def lock(self):
        locked_file = open(self.file_path, 'w')

        try:
            locked_file.write('{0}; started at {1}'.format(os.getpid(), now().isoformat()))
            # try to lock a file
            fcntl.lockf(locked_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise Exception('The process is already running')
        else:
            self.locked_file = locked_file
