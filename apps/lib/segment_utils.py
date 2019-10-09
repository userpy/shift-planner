from apps.lib.utils import daysrange, dtime_interval_to_dates, must_be_datetimes
from collections import defaultdict
from datetime import datetime, timedelta
from django.utils.timezone import get_current_timezone


def check_week_and_day(segments, days_count):
    for i, segm in enumerate(segments):
        day_offset = (segm.week-1)*7 + segm.day
        if day_offset > days_count:
            raise ValueError('wrong segment (%d) week+day offset: %dw+%dd=%d, pattern has %d day(s)'
                             % (i, segm.week, segm.day, day_offset, days_count))


def check_duration_intersection(segments):
    for i in range(1, len(segments)):
        prev, cur = segments[i-1], segments[i]
        if prev.seconds_offset() + prev.duration > cur.seconds_offset():
            raise ValueError('segment (%d) ends after next segment (%d) starts: %s + %gm > %s'
                             % (i-1, i, prev.start_time.strftime('%H:%M'), prev.duration/60, cur.start_time.strftime('%H:%M')))


def check_duration_wrap_intersection(segments, days_count):
    if len(segments) > 1:
        first, last = segments[0], segments[-1]
        if last.seconds_offset() + last.duration - days_count*24*3600 > first.seconds_offset():
            raise ValueError('last segment wraps and ends after first segment starts: %s + %gm > %s'
                             % (last.start_time.strftime('%H:%M'), last.duration/60, first.start_time.strftime('%H:%M')))


def group_by_day_offset(segments, pattern_days_number):
    """ Группирует сегменты по смещению (в днях) от начала первой недели шаблона.
        Если сегмент переходит через 00:00, он попадает в две группы.
        pattern_days_number - кол-во дней в шаблоне. """
    groups = defaultdict(list)

    for segm in segments:
        offset = segm.days_offset()
        groups[offset].append((False, segm))
        if segm.goes_through_midnight():
            offset = offset+1 if offset+1 < pattern_days_number else 0
            groups[offset].append((True, segm))

    return groups


# days_offset - дополнительный сдвиг шаблона в днях (например avail_history.days_offset())
def get_intervals(segments, start_dtime, end_dtime, days_number, day_offset_func,
                  clamp_segments=True, filter_by_start_only=False):
    """ Возвращает части сегментов шаблона в определённом интервале.
        days_number - количество дней в шаблоне (например avail_pattern.days_number)
        day_offset_func(day) - функция, возвращающая отступ переданного дня от начала паттерна
                               (например avail_history.get_day_offset(day)) """
    must_be_datetimes(start_dtime, end_dtime)

    current_tz = get_current_timezone()
    start_date, end_date = dtime_interval_to_dates(start_dtime, end_dtime)
    segments_by_day_offset = group_by_day_offset(segments, days_number)
    prev_segment_and_day = None

    for day in daysrange(start_date, end_date, include_last=True):
        cur_day_offset = day_offset_func(day)

        for is_from_prev_day, segment in segments_by_day_offset[cur_day_offset]:
            if is_from_prev_day and filter_by_start_only:
                continue

            start_day = day
            # если этот сегмент начинается в прошлом дне, но переходит через 00:00
            if is_from_prev_day:
                start_day -= timedelta(days=1)

            # чтоб переходящие через полночь сегменты не повторялись
            if (segment, start_day) == prev_segment_and_day:
                continue
            prev_segment_and_day = (segment, start_day)

            # считаем, что avail.start_time хранится в текущей таймзоне
            segment_start = current_tz.localize(datetime.combine(start_day, segment.start_time))  # TODO: timezones
            segment_end = segment_start + timedelta(seconds=segment.duration)
            # сегменты при необходимости обрезаются
            if clamp_segments:
                segment_start = max(segment_start, start_dtime)
                segment_end = min(segment_end, end_dtime)
            # если сегмент вообще за пределами общего интервала
            if segment_start >= end_dtime or segment_end <= start_dtime:
                continue
            yield segment_start, segment_end, segment
