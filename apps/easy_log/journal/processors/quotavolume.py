# coding=utf-8;

from apps.easy_log.settings import ACTIONS
from apps.easy_log.journal.processors.base import BaseProcessor


class QuotaVolumeProcessor(BaseProcessor):

    APPLIED_ACTIONS = (
        ACTIONS.QUOTA_VOL_NEW,
        ACTIONS.QUOTA_VOL_EDIT,
        ACTIONS.QUOTA_VOL_DEL,
    )

    def get_action_handler_dict(self):
        return {}

    def get_post_process_data_handler_dict(self):
        return {
            ACTIONS.QUOTA_VOL_NEW: self.set_quota_vol_new_value,
            ACTIONS.QUOTA_VOL_EDIT: self.set_quota_vol_edit_value,
            ACTIONS.QUOTA_VOL_DEL: self.set_quota_vol_del_value,
        }

    @staticmethod
    def set_quota_vol_new_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_quota_vol_edit_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data

    @staticmethod
    def set_quota_vol_del_value(data):
        data['value'] = {
            'store_area': data['data']['store_area'],
            'start': data['data']['start'],
            'end': data['data']['end'],
        }
        return data
