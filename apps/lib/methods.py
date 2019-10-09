#
# Copyright 2018 ООО «Верме»
#
# Бибилиотека прикладных функций для облегчения кода
#

from rest_framework import status
from rest_framework.response import Response

def make_error_response(message):
    print('Make_error_response')
    """
    Формирует сообщение об ошибке на основе переданной строки
    """
    return Response({'non_field_errors': message}, status=status.HTTP_400_BAD_REQUEST)

def make_pagination(query_set, page=1, perpage=10):
    """Пагинация и формирования мета информации"""
    total = query_set.count()
    """Определяем отображаемую страницу и объекты на ней"""
    page = int(page)
    perpage = int(perpage)
    pages = int(total / perpage) + 1  # всего страниц
    if page > pages:
        page = 1
    first_record = (page - 1) * perpage  # с какой записи брать
    last_record = first_record + perpage  # и по какую
    query_set = query_set[first_record:last_record]
    meta = {'total': total,
            'pages': pages,
            'page': page,
            'perpage': perpage}
    return query_set, meta

def make_sort(query_set, sort_fields=[], sort_field=None, sort_order=None):
    """Сортировка результатов"""
    if sort_field and sort_field in sort_fields and sort_order:
        if sort_order == 'asc':
            query_set = query_set.order_by(sort_field)
        else:
            query_set = query_set.order_by('-' + sort_field)
    else:
        query_set = query_set.order_by('-id')
    return query_set