import json
import logging
import urllib.parse
import urllib.request

from datetime import date, datetime

from .models import NotifyItem
from apps.lib.utils import add_basic_auth_header, send_sentry_exception, PidLockManager

from apps.remotes.models import RemoteService

logger = logging.getLogger(__name__)


_RESPONSE_STATUS_OK = 'ok'
_RESPONSE_STATUS_ERROR = 'error'


def serialize_json_field(obj):
    if isinstance(obj, datetime) or isinstance(obj, date):
        return obj.isoformat()
    return obj


class NotifyItemProcessor(object):
    """ Парсер таблицы объектов оповещений """

    PID_FILENAME = 'notifications_processor'

    def __init__(self):
        self._employees_cache = {}

    def process(self):
        pid_manager = PidLockManager(self.PID_FILENAME)
        pid_manager.lock()

        items = NotifyItem.objects.filter(status=NotifyItem.STATUS_PENDING)

        for item in items:

            notif_params = []
            notif_params.append((NotifyItem.SEND_METHOD_EMAIL, item.email))

            if len(notif_params) == 0:
                item.status = NotifyItem.STATUS_SKIP
                item.save()
            else:
                item.status = NotifyItem.STATUS_PROCESS
                try:
                    for send_method, send_address in notif_params:
                        self.send(send_method, send_address, item)
                    item.status = NotifyItem.STATUS_DONE
                except Exception as e:
                    logger.exception('NotifyItem sending failed:')
                    send_sentry_exception()
                    item.status = NotifyItem.STATUS_FAIL
                    item.error_text = str(e)
                    break
                finally:
                    item.save()

    def send(self, method, address, item):
        data = {
            'send_method': method,
            'address_to': address,
            'slug': item.template_slug + '_' + method,
            'params': {
                'addressee': {
                    'email': item.email,
                    'full_name': item.full_name,
                }
            },
        }
        data['params'].update(item.params)

        try:
            mailer_service = RemoteService.objects.get(code='MailerService')
        except:
            Exception("The mailer service does not exist")
        url = '{}/{}/'.format(mailer_service.endpoint, mailer_service.action)
        login = mailer_service.login
        password = mailer_service.password

        bytes_data = json.dumps(data, default=serialize_json_field).encode('utf8')
        req = urllib.request.Request(url, data=bytes_data)

        req.add_header("Content-Type", "application/json")
        add_basic_auth_header(req, login, password)
        response = urllib.request.urlopen(req)

        json_data = json.loads(response.read().decode('utf-8'))
        status = json_data.get('result', _RESPONSE_STATUS_ERROR).lower()

        if status != _RESPONSE_STATUS_OK:
            raise Exception('Employee notifier: put item {} to queue failed.'.format(item.id))
