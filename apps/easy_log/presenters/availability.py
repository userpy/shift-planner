# coding=utf-8;

from apps.easy_log.presenters.base import BasePresenter
from apps.easy_log.settings import ACTIONS, LOG_SHORT_DATE_FORMAT, LOG_SHORT_DATETIME_FORMAT


class AvailabilityNewPresenter(BasePresenter):
    action = ACTIONS.AVAIL_NEW

    @staticmethod
    def get_agency_name(agency_name):
        result = agency_name
        if not result:
            result = '-'
        return result

    @property
    def description(self):
        store_area = self._json_data['value'].get('store_area', '--')
        start = self._json_data['value']['start']
        end = self._json_data['value']['end']

        out = f"Доступность в {store_area} c {start} по {end}"
        diff = self._json_data.get('value', {}).get('diff')

        if diff:
            out += ':\n'

            if diff.get('agency'):
                value_from = self.get_agency_name(diff['agency']['from'])
                value_to = self.get_agency_name(diff['agency']['to'])
                out += f'- агентство: {value_from} -> {value_to}\n'

            if diff.get('start'):
                value_from = diff['start']['from']
                value_to = diff['start']['to']
                out += f'- дата начала: {value_from} -> {value_to}\n'

            if diff.get('end'):
                value_from = diff['end']['from']
                value_to = diff['end']['to']
                out += f'- дата окончания: {value_from} -> {value_to}\n'

        return out


class AvailabilityEditPresenter(AvailabilityNewPresenter):
    action = ACTIONS.AVAIL_EDIT


class AvailabilityDelPresenter(AvailabilityNewPresenter):
    action = ACTIONS.AVAIL_DEL
