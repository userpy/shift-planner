# coding=utf-8;

from apps.easy_log.presenters.base import BasePresenter
from apps.easy_log.settings import ACTIONS, LOG_SHORT_DATE_FORMAT, LOG_SHORT_DATETIME_FORMAT


class QuotaVolumeNewPresenter(BasePresenter):
    action = ACTIONS.QUOTA_VOL_NEW

    @property
    def description(self):
        store_area = self._json_data['value'].get('store_area', '--')
        start = self.get_localtime_formatted_date(self._json_data['value']['start'])
        try:
            end = self.get_localtime_formatted_date(self._json_data['value']['end'])
        except TypeError:
            end = None
        out = f"Ограничение квоты в {store_area} c {start.strftime(LOG_SHORT_DATE_FORMAT)} по {end.strftime(LOG_SHORT_DATE_FORMAT) if end else '-'}"
        diff = self._json_data.get('value', {}).get('diff')

        if diff:
            out += ':\n'

            if diff.get('start'):
                value_from = self.get_localtime_formatted_date(diff['start']['from']).strftime(LOG_SHORT_DATE_FORMAT)
                value_to = self.get_localtime_formatted_date(diff['start']['to']).strftime(LOG_SHORT_DATE_FORMAT)
                out += f'- дата начала: {value_from} -> {value_to}\n'

            if diff.get('end'):
                value_from = self.get_localtime_formatted_date(diff['end']['from']).strftime(LOG_SHORT_DATE_FORMAT) if diff['end'].get('from') else '-'
                value_to = self.get_localtime_formatted_date(diff['end']['to']).strftime(LOG_SHORT_DATE_FORMAT) if diff['end'].get('from') else '-'
                out += f'- дата окончания: {value_from} -> {value_to}\n'

            if diff.get('value'):
                value_from = diff['value']['from']
                value_to = diff['value']['to']
                out += f'- максимум: {value_from} -> {value_to}\n'

        return out


class QuotaVolumeEditPresenter(QuotaVolumeNewPresenter):
    action = ACTIONS.QUOTA_VOL_EDIT


class QuotaVolumeDelPresenter(QuotaVolumeNewPresenter):
    action = ACTIONS.QUOTA_VOL_DEL

