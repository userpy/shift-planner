from abc import ABCMeta, abstractproperty

from django.utils import timezone

from apps.easy_log.settings import LOG_DATETIME_FORMAT, LOG_SHORT_DATE_FORMAT


class BasePresenter:

    __metaclass__ = ABCMeta

    action = None

    def __init__(self, json_obj):
        self._json_data = json_obj

    def get_formatted_date(self, value):
        import datetime
        if not value:
            return
        try:
            dt = datetime.datetime.strptime(value, LOG_DATETIME_FORMAT)
        except ValueError:
            dt = datetime.datetime.strptime(value, LOG_SHORT_DATE_FORMAT)
        dt = dt.replace(tzinfo=timezone.utc)
        return dt

    def get_localtime_formatted_date(self, value):
        if value:
            return timezone.localtime(self.get_formatted_date(value))

    def get_obj_attr_or_id(self, model, pk, attr, id_str='ID=%s'):
        obj = model.objects.filter(pk=pk).last()
        return getattr(obj, attr) if obj is not None else (id_str % pk)

    @abstractproperty
    def description(self):
        pass
