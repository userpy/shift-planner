from apps.easy_log.presenters.base import BasePresenter
from apps.easy_log.settings import ACTIONS
from django.utils.html import format_html


class LogoutPresenter(BasePresenter):

    action = ACTIONS.LOGOUT

    @property
    def description(self):
        return format_html("Пользователь '{}' (#{})<br>{}",
                           self._json_data['value'].get('username'),
                           self._json_data.get('user_id'),
                           self._json_data['value'].get('useragent', ''))
