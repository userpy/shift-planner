# coding=utf-8;

from apps.easy_log.settings import ACTIONS
from apps.easy_log.journal.processors.base import BaseProcessor


class QuotaProcessor(BaseProcessor):

    APPLIED_ACTIONS = (
        ACTIONS.QUOTA_NEW,
        ACTIONS.QUOTA_EDIT,
        ACTIONS.QUOTA_DEL,
    )

    def get_action_handler_dict(self):
        return {}

    def get_post_process_data_handler_dict(self):
        return {
            ACTIONS.QUOTA_NEW: self.set_quota_new_value,
            ACTIONS.QUOTA_EDIT: self.set_quota_edit_value,
            ACTIONS.QUOTA_DEL: self.set_quota_del_value,
        }

    @staticmethod
    def set_quota_new_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'value_total': data['data']['value_total'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_quota_edit_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'value_total': data['data']['value_total'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_quota_del_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'value_total': data['data']['value_total'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data
