# coding=utf-8;

import logging
from json import dumps, JSONEncoder
from datetime import datetime, date

__all__ = ['multiplayer_log']


class DateTimeEncoder(JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime):
            return {
                '__type__': 'datetime',
                'year': obj.year,
                'month': obj.month,
                'day': obj.day,
                'hour': obj.hour,
                'minute': obj.minute,
                'second': obj.second,
                'microsecond': obj.microsecond,
            }
        if isinstance(obj, date):
            return {
                '__type__': 'date',
                'year': obj.year,
                'month': obj.month,
                'day': obj.day,
            }

        else:
            return JSONEncoder.default(self, obj)


logger = logging.getLogger('multiplayer')


def multiplayer_log(message, params):
    user = params.pop('user_for_log', 'Unknown')
    msg = '{}\nUser: {}\n{}'.format(message,
                                    user,
                                    dumps(params, cls=DateTimeEncoder))
    logger.warning(msg)