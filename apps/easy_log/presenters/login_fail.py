from apps.easy_log.presenters.base import BasePresenter
from apps.easy_log.settings import ACTIONS
from django.utils.html import format_html


class LoginFailPresenter(BasePresenter):

    action = ACTIONS.LOGIN_FAIL

    @property
    def description(self):
        reason = self._json_data['value'].get('reason')
        if reason is None:
            found = self._json_data['value'].get('user_was_found')
            if found is True:
                reason = 'Неверный пароль'
            elif found is False:
                reason = 'Пользователь не найден'
            elif found is None:
                reason = 'Неверные учётные данные'
            else:
                reason = '???'

        credentials_info = []
        for attr in ['email', 'phone', 'username']:
            if attr in self._json_data['value'].get('credentials', {}):
                credentials_info.append(f"{attr}: {self._json_data['value']['credentials'][attr]}")

        credentials = ', '.join(credentials_info)
        if len(credentials_info) == 0:
            credentials = self._json_data['value'].get('credentials')

        useragent = self._json_data['value'].get('useragent', '')

        return format_html("{}, {}<br>{}", reason, credentials, useragent)
