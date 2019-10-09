import datetime

from django.db import models
from django.utils.timezone import get_current_timezone

from .constants import EXCEL_COLORS


class ExcelColorMixin(models.Model):
    EXCEL_COLOR_CHOICES = [(i, i.replace('_', ' ')) for i in EXCEL_COLORS]

    excel_color = models.CharField('Палитра цветов для excel', max_length=30,
                                   choices=EXCEL_COLOR_CHOICES, blank=True, null=True)

    class Meta:
        abstract = True


class ConvertTimezoneMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        names = []
        for field, value in self.__dict__.items():
            if isinstance(value, datetime.datetime):
                names.append(field)

        for name in names:
            self.make_datetime_attr(name)

    def get_department(self):
        return self.department

    def make_datetime_attr(self, name):
        tz = self.get_department().get_timezone()
        value = getattr(self, name)
        dtime_msc = value.astimezone(get_current_timezone()).utcoffset()
        dtime = value.astimezone(tz).utcoffset()
        diff = dtime - dtime_msc
        new_dtime = value - datetime.timedelta(seconds=diff.seconds)
        setattr(self, '{0}_tz'.format(name), new_dtime.astimezone(tz))
