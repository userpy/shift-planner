# coding=utf-8;

from apps.easy_log.settings import ACTIONS
from apps.easy_log.journal.processors.base import BaseProcessor


class AuthProcessor(BaseProcessor):

    APPLIED_ACTIONS = (
        ACTIONS.LOGIN,
        ACTIONS.LOGIN_FAIL,
        ACTIONS.LOGOUT,
    )

    def get_action_handler_dict(self):
        return {}

    def get_post_process_data_handler_dict(self):
        return {
            ACTIONS.LOGIN: self.set_login_value,
            ACTIONS.LOGIN_FAIL: self.set_login_fail_value,
            ACTIONS.LOGOUT: self.set_logout_value,
        }

    @staticmethod
    def set_login_value(data):
        data['value'] = {
            'username': data['data']['username'],
            'useragent': data['data']['useragent'],
            'authmethod': data['data'].get('authmethod'),
        }
        return data

    @staticmethod
    def set_login_fail_value(data):
        data['value'] = {
            'reason': data['data']['reason'],
            'credentials': data['data']['credentials'],
            'user_was_found': data['data']['user_was_found'],
            'useragent': data['data']['useragent'],
        }
        return data

    @staticmethod
    def set_logout_value(data):
        data['value'] = {
            'username': data['data']['username'],
            'useragent': data['data']['useragent'],
        }
        return data
