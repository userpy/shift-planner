# coding=utf-8;

from apps.easy_log.settings import ACTIONS
from apps.easy_log.journal.processors.base import BaseProcessor


class PromoShiftProcessor(BaseProcessor):

    APPLIED_ACTIONS = (
        ACTIONS.PROMO_SHIFT_NEW,
        ACTIONS.PROMO_SHIFT_EDIT,
        ACTIONS.PROMO_SHIFT_DEL,
    )

    def get_action_handler_dict(self):
        return {}

    def get_post_process_data_handler_dict(self):
        return {
            ACTIONS.PROMO_SHIFT_NEW: self.set_promo_shift_new_value,
            ACTIONS.PROMO_SHIFT_EDIT: self.set_promo_shift_edit_value,
            ACTIONS.PROMO_SHIFT_DEL: self.set_promo_shift_del_value,
        }

    @staticmethod
    def set_promo_shift_new_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_promo_shift_edit_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_promo_shift_del_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data
