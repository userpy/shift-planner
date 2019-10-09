#
# Copyright 2018 ООО «Верме»
#
# Декораторы для проверки прав доступа
#

from django.http import HttpResponseRedirect
from django.urls import reverse, resolve
from django.shortcuts import redirect
from .models import Page
from .methods import check_struct_access_to_page, available_pages
from wfm import settings


def make_base_context(function):
    def wrap(request, *args, **kwargs):
        user = request.user

        # Формирование списка страниц
        pages = available_pages(user)
        outsource_enable = False
        client_enable = False
        promo_enable = False
        broker_enable = False
        for page in pages:
            if page.party == 'agency' and not outsource_enable:
                outsource_enable = True
                continue
            if page.party == 'client' and not client_enable:
                client_enable = True
                continue
            if page.party == 'promo' and not promo_enable:
                promo_enable = True
                continue
            if page.party == 'broker' and not broker_enable:
                broker_enable = True
                continue
        base_context = {'outsource_enable': outsource_enable,
                        'client_enable': client_enable,
                        'promo_enable': promo_enable,
                        'broker_enable': broker_enable,
                        'pages': pages,
                        'DEBUG': settings.DEBUG}
        kwargs.update(base_context)
        return function(request, *args, **kwargs)
    return wrap


def check_page_permission_by_user(function):
    @make_base_context
    def wrap(request, *args, **kwargs):
        user = request.user
        # Получаем текущую страницу
        url_name = resolve(request.path).url_name
        page = Page.objects.filter(code=url_name).first()
        if not page:
            return HttpResponseRedirect(reverse('no_page'))

        # Сохрнаяем информацию о текущей и базовой страницах в объект запроса
        #TODO - Странно видеть сохранение информации в функции проверке прав доступа
        request.page = page
        if page.parent:
            request.base_page = page.parent
        else:
            request.base_page = page
 
        #TODO - в текущей реализации отсутствует контекст выбранной организации, что не корректно
        #       в дальнейшем следует переработать так, чтобы любой запрос содержал клиента 
        if check_struct_access_to_page(user, None, None, page, 'read'):
            return function(request, *args, **kwargs)
        else:
            return redirect(reverse('no_access'))
    return wrap


