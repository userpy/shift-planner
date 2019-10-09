import traceback

from apps.easy_log.settings import EASY_LOG
from apps.lib.utils import PidLockManager


class JournalProcessor:

    def handle(self):
        """ Основная точка входа в журнал событий """
        reader = self.get_reader()
        if EASY_LOG['RUN_UNIQUE']:
            pid_manager = PidLockManager(EASY_LOG['FILENAME'])
            pid_manager.lock()

        step = 0
        while step < EASY_LOG['ROWS_PER_ACTION']:
            try:
                row_data = reader.read()
                if not row_data:
                    break

                processor = self.get_processor(row_data)
                result = processor.process(row_data)
                if result and row_data['is_atomic']:
                    reader.remove_row(row_data['row_id'])
            except Exception as exc:
                traceback.print_exc()
                reader._mark_row_failed(row_data['row_id'])
                # TODO: Эту ситуацию нужно логировать
                break

    @staticmethod
    def get_reader():
        """  Получаем "читальщика" данных """
        from apps.easy_log.journal.readers import all_readers

        all_readers_dict = dict((r.TYPE_NAME, r) for r in all_readers)
        reader_cls = all_readers_dict[EASY_LOG['READER']]
        return reader_cls()

    @staticmethod
    def get_processor(data):
        """ Возвращает процессор данных по его action """
        from apps.easy_log.journal.processors import all_processors

        all_processors_dict = dict(
            (p.APPLIED_ACTIONS, p) for p in all_processors
        )
        for actions_list, processor_cls in all_processors_dict.items():
            if data['action'] in actions_list:
                return processor_cls(data['action'])
