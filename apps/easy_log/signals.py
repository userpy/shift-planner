from django.contrib.auth import signals as auth_signals
from apps.easy_log.settings import SOURCE
from apps.easy_log.shortcuts import log_login, log_login_fail, log_logout


def _get_source_by_path(path_info):
    if path_info.startswith('/admin/'):
        return SOURCE.DJANGO
    # elif path_info.startswith('/saml/'):
    #     return SOURCE.EXTERNAL
    return SOURCE.PORTAL


def on_django_login(sender, request, user, *args, **kwargs):
    authmethod = None
    attrs = getattr(request, 'login_details', {})
    if 'user_found_by_LDAP' in attrs and attrs['user_found_by_LDAP'] is True:
        authmethod = 'LDAP'
    if 'user_found_by_SAML' in attrs and attrs['user_found_by_SAML'] is True:
        authmethod = "SAML"

    log_login(user_id=user.id,
              source_info=request.COOKIES.get('sessionid', 'no cookie'),
              source=_get_source_by_path(request.META.get('PATH_INFO', '')),
              username=user and user.username,
              useragent=request.META.get('HTTP_USER_AGENT'),
              authmethod=authmethod)

auth_signals.user_logged_in.connect(on_django_login)


def on_django_logout(sender, request, user, *args, **kwargs):
    log_logout(user_id=user and user.id,
               source_info=request.COOKIES.get('sessionid', 'no cookie'),
               source=_get_source_by_path(request.META.get('PATH_INFO', '')),
               username=user and user.username,
               useragent=request.META.get('HTTP_USER_AGENT'))

auth_signals.user_logged_out.connect(on_django_logout)


def on_django_login_fail(sender, credentials, request, *args, **kwargs):
    log_login_fail(source_info=request.COOKIES.get('sessionid', 'no cookie'),
                   reason=None,
                   credentials=credentials,
                   user_was_found=getattr(request, 'login_details', {}).get('user_found'),
                   useragent=request.META.get('HTTP_USER_AGENT'))

auth_signals.user_login_failed.connect(on_django_login_fail)
