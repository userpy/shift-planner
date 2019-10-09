from apps.easy_log.settings import LOG_DATETIME_FORMAT, LOG_SHORT_DATE_FORMAT
# from datetime import datetime


def model_choices_to_dict(choices):
    """ Convert django model choices tuple to dict """
    return dict((item[0], item[1]) for item in choices)


def strftime(time):
    return time.strftime(LOG_DATETIME_FORMAT)


# def strptime(string):
#     return datetime.strptime(string, LOG_DATETIME_FORMAT)


def strftime_short_date(time):
    return time.strftime(LOG_SHORT_DATE_FORMAT)


# def strftime_short_date_or(time, none_string):
#     if time is None:
#         return none_string
#     return strftime_short_date(time)
