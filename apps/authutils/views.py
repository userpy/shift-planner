import json

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.forms.utils import ErrorList
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View
from apps.lib.http import JsonError, JsonOk, JsonUserDisplayErrorExt
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect

from axes.attempts import is_already_locked
from axes.utils import get_lockout_message


def axes_username_getter(request, credentials):
    """ Возвращает для axes'а имя пользователя из запроса.
        Ищет по credentials (если передан), по данным POST-запроса или по JSON'овому телу запроса. """
    if credentials is not None:
        for attr in ['username', 'login', 'email']:
            if attr in credentials:
                return credentials[attr]

    for attr in ['username', 'login', 'email']:
        if attr in request.POST:
            return request.POST[attr]

    try:
        data = json.loads(request.body.decode('utf-8'))
    except ValueError as e:
        pass
    else:
        if 'login' in data:
            return data['login']

    return None


def lockout_response_ext(request):
    """ Переопределённый axes'овый lockout_response, возвращает JSON-ошибку в нужном виде. """
    if request.is_ajax():
        return JsonUserDisplayErrorExt(403, 'auth:floodwait', message=get_lockout_message())

    if settings.AXES_LOCKOUT_TEMPLATE:
        return render(request, settings.AXES_LOCKOUT_TEMPLATE, context={}, status=403)

    if settings.AXES_LOCKOUT_URL:
        return HttpResponseRedirect(settings.AXES_LOCKOUT_URL)

    return HttpResponse(get_lockout_message(), status=403)


def axes_dispatch_ext(func):
    """ Переопределённый axes'овый axes_dispatch, нужен для собственного lockout_response. """
    def inner(request, *args, **kwargs):
        if is_already_locked(request):
            return lockout_response_ext(request)
        return func(request, *args, **kwargs)
    return inner


class LoginForm(forms.Form):
    login = forms.CharField()
    password = forms.CharField()

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

    def clean(self):
        if self._errors:
            return

        params = {'password': self.cleaned_data['password'],
                  'email': self.cleaned_data['login'],
                  'request': self.request
                  }
        user = authenticate(**params)

        if user is None:
            self._errors = ErrorList(['Имя пользователя или пароль введены некорректно'])
        elif not user.is_active:
            self._errors = ErrorList(['Пользователь заблокирован'])
        else:
            self.user = user


@method_decorator(axes_dispatch_ext, name='dispatch')
class LoginView(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        return render(request, 'base/user/login.html', {'saml_idps': getattr(settings, 'SOCIAL_AUTH_SAML_ENABLED_IDPS', {})})

    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except ValueError as e:
            return JsonError('json parsing error %s' % e.args[0])

        form = LoginForm(data, request=request)
        if not form.is_valid():
            message = ', '.join(form.errors) if isinstance(form.errors, ErrorList) else str(dict(form.errors))
            return JsonUserDisplayErrorExt(403, 'auth:login_fail', message=message)

        login(request, form.user)
        return JsonOk()


def logout_view(request):
    logout(request)
    return JsonOk()
