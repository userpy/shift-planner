from django.core.management import call_command
from django.core.management.base import BaseCommand

from apps.lib.decorators import command_error_logger


class Command(BaseCommand):
    commands = ['run_notifier', 'run_log_journal', 'update_docs_files_info']
    help = 'Последовательно запускает комманды: ' + ', '.join(commands)

    def add_arguments(self, parser):
        parser.add_argument('--debug', type=bool, default=False, help='режим отладки')

    @command_error_logger
    def handle(self, *args, **options):
        for cmd in self.commands:
            getattr(self, '_call_' + cmd)(options)

    def _call_run_notifier(self, options):
        call_command('run_notifier')

    def _call_run_log_journal(self, options):
        call_command('run_log_journal')

    def _call_update_docs_files_info(self, options):
        call_command('update_docs_files_info')


