#
# Copyright 2018 ООО «Верме»
#
# Информация по загруженным файлам
#

# coding=utf-8;

from django.core.management.base import BaseCommand
from apps.remotes.models import RemoteService
from apps.employees.models import EmployeeDoc
from apps.employees.methods import make_docs_params
from django.contrib.auth.models import User
import datetime
import json


class Command(BaseCommand):
    help = 'Updates files info from docs'

    def handle(self, *args, **options):
        # - не заданы параметры доступа к Порталу Внешнего Персонала
        docs_service = RemoteService.get_service('VermeDocs')
        if not docs_service:
            return
        files_sync_timestamp = docs_service.get_param('file_sync_timestamp',
                                                 datetime.datetime(2018, 1, 1).isoformat())
        current_user = User.objects.filter(username='mvideo').first()
        if not current_user:
            return

        """Получение guid документов для запроса"""
        doc_guids = []

        docs = EmployeeDoc.objects.filter(doc_type__code='medical',
                                          dt_change__gt=files_sync_timestamp).order_by('dt_change')
        for doc in docs:
            doc_guids.append(str(doc.guid))

        # Формируем и отправляем запрос на сервис docs со списком guid требуемых документов
        str_guids = ','.join(doc_guids)
        docs_params = make_docs_params(current_user, str_guids)
        response = docs_service.send_sync_json_request(docs_params,
                                                       'check',
                                                       entity_guids=json.dumps(doc_guids),
                                                       format='json')
        if response:
            if response['type'] == 'success':
                for entity in response['entity_guids']:
                    EmployeeDoc.objects.filter(guid=entity['guid']).update(has_files=entity['has_files'])
                    #print('updated', entity['guid'], entity['has_files'])
                docs_service.update_params(file_sync_timestamp=docs[0].dt_change.isoformat())