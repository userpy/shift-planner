# coding=utf-8;

from apps.easy_log.settings import ACTIONS
from apps.easy_log.journal.processors.base import BaseProcessor


class AvailabilityProcessor(BaseProcessor):

    APPLIED_ACTIONS = (
        ACTIONS.AVAIL_NEW,
        ACTIONS.AVAIL_EDIT,
        ACTIONS.AVAIL_DEL,
    )

    def get_action_handler_dict(self):
        return {}

    def get_post_process_data_handler_dict(self):
        return {
            ACTIONS.AVAIL_NEW: self.set_avail_new_value,
            ACTIONS.AVAIL_EDIT: self.set_avail_edit_value,
            ACTIONS.AVAIL_DEL: self.set_avail_del_value,
        }

    @staticmethod
    def set_avail_new_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_avail_edit_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_avail_del_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data
