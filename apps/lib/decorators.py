import logging
import re

from decorator import decorator


logger = logging.getLogger('command')


@decorator
def command_error_logger(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        # превращаем что-то длинное типа 'apps.worktime.management.commands.analyse_worktime' в 'analyse_worktime'
        m = re.search(r'[^.]*$', func.__module__)
        method = func.__module__ if m is None else m.group(0)
        kwargs.update({'source': 'command', 'method': method})
        logger.error(str(e), extra={'params': kwargs})
        raise e
