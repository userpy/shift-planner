# coding=utf-8;

from apps.easy_log.settings import ACTIONS
from apps.easy_log.journal.processors.base import BaseProcessor


class OutsourcingShiftProcessor(BaseProcessor):

    APPLIED_ACTIONS = (
        ACTIONS.OUT_SHIFT_NEW,
        ACTIONS.OUT_SHIFT_EDIT,
        ACTIONS.OUT_SHIFT_DEL,
    )

    def get_action_handler_dict(self):
        return {}

    def get_post_process_data_handler_dict(self):
        return {
            ACTIONS.OUT_SHIFT_NEW: self.set_out_shift_new_value,
            ACTIONS.OUT_SHIFT_EDIT: self.set_out_shift_edit_value,
            ACTIONS.OUT_SHIFT_DEL: self.set_out_shift_del_value,
        }

    @staticmethod
    def set_out_shift_new_value(data):
        data['value'] = {
            'job': data['data']['job'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_out_shift_edit_value(data):
        data['value'] = {
            'job': data['data']['job'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_out_shift_del_value(data):
        data['value'] = {
            'job': data['data']['job'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data
