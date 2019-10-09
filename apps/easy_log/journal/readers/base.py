# coding=utf-8;

from abc import ABCMeta, abstractmethod, abstractproperty


class BaseReader:

    __metaclass__ = ABCMeta

    @abstractproperty
    def TYPE_NAME(self):
        """ Уникальное имя "читальщика" """
        pass

    def read(self):
        """ Метод, читающий строку из потока данных и возвращающий эти данные
                в определенной структуре """

        source_dict = self._read_single_row()
        if source_dict == {}:
            return

        if not source_dict:
            return
        return self.object_to_dict(source_dict)

    def object_to_dict(self, source):
        """ Переводим "сырой объект" в словарь определенной структуры """
        if not source:
            return None

        return {
            "row_id": source["row_id"],
            "created": source['created'],
            "action": source['action'],
            "is_atomic": source['is_atomic'],
            "process_id": source['process_id'],
            "data": source['data'],
            "status": source['status'],
        }

    @abstractmethod
    def _read_single_row(self):
        """ Абстрактный метод, читающий одну строку из потока данных """
        pass

    @abstractmethod
    def _mark_row_failed(self, row_id):
        """ Абстрактный метод, помечающий строку как обработканоотправлено в работу """
        pass

    @abstractmethod
    def remove_row(self, row_id):
        """ Абстрактный метод, удаляющий одну строку из потока данных """
        pass
