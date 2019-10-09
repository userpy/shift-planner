# coding=utf-8;

from apps.easy_log.settings import JOURNAL_STATUS, LOG_DATETIME_FORMAT
from apps.easy_log.journal.readers.base import BaseReader
from apps.easy_log.models import LogJournal


class DBReader(BaseReader):

    TYPE_NAME = 'DB'

    def _read_single_row(self):
        result = {}

        obj = LogJournal.objects.order_by('id').first()

        if obj:
            result = {
                "row_id": obj.id,
                "created": obj.created.strftime(LOG_DATETIME_FORMAT),
                "process_id": obj.process_id,
                "status": obj.status,
                "data": obj.data,
                "action": obj.action,
                "is_atomic": obj.is_atomic,
            }
        return result

    def _mark_row_in_progress(self, row_id):
        LogJournal.objects.filter(pk=row_id).update(
            status=JOURNAL_STATUS.PROCESS
        )

    def _mark_row_fail(self, row_id):
        LogJournal.objects.filter(pk=row_id).update(
            status=JOURNAL_STATUS.FAIL
        )

    def remove_row(self, row_id):
        LogJournal.objects.get(pk=row_id).delete()