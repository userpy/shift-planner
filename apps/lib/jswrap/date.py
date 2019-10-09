# coding=utf-8;

"""
Модуль содержит реализацию класса для работы
с датами в формате милисекунд.

По-сути модуль является аналогом
js-объекта utils.js:Date
"""

from datetime import datetime, timedelta


class Date(object):

    second = 1000
    minute = second * 60
    hour = minute * 60
    day = hour * 24
    week = day * 7

    @staticmethod
    def start_of_day(value):
        return datetime(year=value.year,
                        month=value.month,
                        day=value.day)

    @staticmethod
    def start_of_week(value):
        return Date.start_of_day(value) - timedelta(days=value.weekday())

    @staticmethod
    def end_of_week(value):
        return Date.start_of_day(value) + timedelta(days=6-value.weekday())

    @staticmethod
    def start_of_month(value):
        return Date.start_of_day(value) - timedelta(days=value.day-1)

    @staticmethod
    def end_of_month(value):
        year = value.year
        month = value.month

        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

        return datetime(year=year, month=month, day=1) - timedelta(days=1)

    @staticmethod
    def get_day_time(value):
        return value.hour * Date.hour + value.minute * Date.minute + value.second * Date.second