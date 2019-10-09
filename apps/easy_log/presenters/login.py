from apps.easy_log.presenters.base import BasePresenter
from apps.easy_log.settings import ACTIONS
from django.utils.html import format_html


class LoginPresenter(BasePresenter):

    action = ACTIONS.LOGIN

    @property
    def description(self):
        if 'authmethod' in self._json_data['value'] and self._json_data['value']['authmethod']:
            authmethod = 'Вход через ' + self._json_data['value'].get('authmethod')
        else:
            authmethod = 'Локальный вход'
        return format_html("{}: пользователь '{}' (#{})<br>{}",
                           authmethod,
                           self._json_data['value'].get('username'),
                           self._json_data.get('user_id'),
                           self._json_data['value'].get('useragent', ''))
