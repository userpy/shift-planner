from django.core.management.base import BaseCommand

from apps.easy_log.journal import JournalProcessor


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--debug', type=bool, default=False, help='режим отладки')

    def handle(self, *args, **options):
        JournalProcessor().handle()
