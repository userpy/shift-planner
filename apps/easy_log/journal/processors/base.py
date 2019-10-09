# coding=utf-8;

from abc import ABCMeta, abstractmethod, abstractproperty


class BaseProcessor:

    __metaclass__ = ABCMeta

    def __init__(self, action):
        self.action = action

    @abstractproperty
    def APPLIED_ACTIONS(self):
        """ Список action'ов, которые может обрабатывать """
        return []

    def process(self, data):
        """ Основной метод, в котором и происходит вся "магия" """
        prepared_data = self.prepare_data(data)
        prepared_data = self.get_post_process_data_handler()(prepared_data)

        if prepared_data['is_atomic']:
            self.get_action_handler()(prepared_data)
            self.write_to_db(prepared_data)
            return True
        else:
            # TODO:  Обработка для "пачки" записей в транзакции
            raise NotImplementedError

    def get_action_handler(self):
        return self.get_action_handler_dict().get(self.action,
                                                  lambda data: None)

    @abstractmethod
    def get_action_handler_dict(self):
        """ Возвращаем словарь с обработчиками, которые должны быть запущены
                    в зависимости от action """
        pass

    def get_post_process_data_handler(self):
        return self.get_post_process_data_handler_dict()[self.action]

    @abstractmethod
    def get_post_process_data_handler_dict(self):
        """ Возвращаем словарь с обработчиками данных
            в зависимости от action """
        pass

    @staticmethod
    def prepare_created(prepared_data):
        import datetime
        from django.utils import timezone
        from apps.easy_log.settings import LOG_DATETIME_FORMAT

        created = datetime.datetime.strptime(prepared_data['created'],
                                             LOG_DATETIME_FORMAT)
        created = created.replace(tzinfo=timezone.utc)
        return timezone.localtime(created)

    def write_to_db(self, prepared_data):
        from apps.easy_log.models import LogItem

        if isinstance(prepared_data['value'], dict):
            diff = prepared_data['data'].get('diff', {})
            prepared_data['value'].update({'diff': diff})

        LogItem.objects.create(
            created=self.prepare_created(prepared_data),
            process_id=prepared_data['process_id'],
            source=prepared_data['source'],
            source_info=prepared_data.get('source_info') or '',
            action=prepared_data['action'],
            user_id=prepared_data['user_id'],
            value=prepared_data['value'],
            entity_id=prepared_data.get('entity_id'),
            entity_class=prepared_data.get('entity_class'),
            headquarter=prepared_data.get('headquarter'),
            aheadquarter=prepared_data.get('aheadquarter'),
            organization=prepared_data.get('organization'),
            agency=prepared_data.get('agency')
        )

    def prepare_data(self, data):
        """ Метод, подготавливающий данные к вставке в БД """
        inner_data = data['data']

        return {
            'created': data['created'],
            'process_id': data['process_id'],
            'is_atomic': data['is_atomic'],
            'source': inner_data['source'],
            'source_info': inner_data['source_info'],
            'action': data['action'],
            'user_id': inner_data.get('user_id'),
            'entity_id': inner_data.get('entity_id'),
            'entity_class': inner_data.get('entity_class'),
            'headquarter': inner_data.get('headquarter'),
            'aheadquarter': inner_data.get('aheadquarter'),
            'organization': inner_data.get('organization'),
            'agency': inner_data.get('agency'),
            'value': inner_data.get('value', {}),
            'data': inner_data,
        }
