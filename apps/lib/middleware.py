from django.core.urlresolvers import reverse
from django.shortcuts import render

from ua_parser import user_agent_parser

from apps.config.models import Config


def old_browser_middleware(get_response):
    def major_int_lt(ua, min_major):
        """ Проверяет, не меньше ли версия браузера минимально допустимой.
            В любой непонятной ситуации возвращает False, чтоб случайно не заблокировать лишнего. """
        if ua['major'] is None:
            return False
        try:
            num = int(ua['major'])
        except ValueError:
            return False
        if num < min_major:
            return True
        return False

    def major_int_lt_config(ua, config_name):
        """ Проверяет версию браузера, если в конфиге указана минимальная """
        value = Config.get(config_name)
        if value is None:
            return False
        return major_int_lt(ua, int(value))

    def is_old(ua_string):
        if ua_string is None:
            return False
        ua = user_agent_parser.ParseUserAgent(ua_string)
        if ua['family'] == 'IE' and major_int_lt(ua, 11):
            return True
        if ua['family'] == 'Chrome' and major_int_lt_config(ua, 'ua_min_chrome_version'):
            return True
        if ua['family'] == 'Firefox' and major_int_lt_config(ua, 'ua_min_firefox_version'):
            return True
        if ua['family'] == 'Safari' and major_int_lt_config(ua, 'ua_min_safari_version'):
            return True
        if ua['family'] == 'Yandex Browser' and major_int_lt_config(ua, 'ua_min_yandex_version'):
            return True
        return False

    paths = {reverse('index'), reverse('login')}

    def should_check(path):
        return path in paths

    def middleware(request):
        if should_check(request.path) and is_old(request.META.get('HTTP_USER_AGENT')):
            return render(request, 'old_browser.html')
        return get_response(request)

    return middleware
