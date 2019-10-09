from django.core.management.base import BaseCommand

from apps.easy_log.models import LogJournal
from apps.easy_log.settings import JOURNAL_STATUS


class Command(BaseCommand):
    def handle(self, *args, **options):
        LogJournal.objects.all().update(status=JOURNAL_STATUS.NEW)
