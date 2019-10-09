# coding=utf-8;

from apps.easy_log.presenters.base import BasePresenter
from apps.easy_log.settings import ACTIONS, LOG_SHORT_DATE_FORMAT, LOG_SHORT_DATETIME_FORMAT


class OutShiftNewPresenter(BasePresenter):
    action = ACTIONS.OUT_SHIFT_NEW

    @staticmethod
    def get_shift_employee_name(employee_name):
        result = employee_name
        if not result:
            result = 'Открытая смена'
        return result

    @property
    def description(self):
        job = self._json_data['value'].get('job', '--')
        start = self._json_data['value']['start']
        end = self._json_data['value']['end']

        out = f"Смена в {job} c {start} по {end}"
        diff = self._json_data.get('value', {}).get('diff')

        if diff:
            out += ':\n'

            if diff.get('agency_employee'):
                value_from = self.get_shift_employee_name(diff['agency_employee']['from'])
                value_to = self.get_shift_employee_name(diff['agency_employee']['to'])
                out += f'- сотрудник: {value_from} -> {value_to}\n'

            if diff.get('start'):
                value_from = diff['start']['from']
                value_to = diff['start']['to']
                out += f'- дата начала: {value_from} -> {value_to}\n'

            if diff.get('end'):
                value_from = diff['end']['from']
                value_to = diff['end']['to']
                out += f'- дата окончания: {value_from} -> {value_to}\n'

        return out


class OutShiftEditPresenter(OutShiftNewPresenter):
    action = ACTIONS.OUT_SHIFT_EDIT


class OutShiftDelPresenter(OutShiftNewPresenter):
    action = ACTIONS.OUT_SHIFT_DEL
