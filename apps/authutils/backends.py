from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q
from saml.methods import set_user_login_details


class EmailLoginBackend(ModelBackend):
    """ Логинит пользователей по почте и паролю. """
    def authenticate(self, request, email=None, password=None, **kwargs):
        if not email or not password:
            return None

        set_user_login_details(request, 'email', False)

        # Учетная запись пользователя определяется по email либо по логину
        user = User.objects.filter(email=email).last()
        if user is None:
            user = User.objects.filter(username=email).last()

        if user is None:
            return None

        set_user_login_details(request, 'email', True)

        if not user.check_password(password):
            return None
        return user


class UsernameLoginBackend(ModelBackend):
    """ Логинит пользователей по имени и паролю (для суперпользователей в админке). """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        set_user_login_details(request, 'username', False)

        user = User.objects.filter(Q(username=username), Q(is_superuser=True) | Q(is_staff=True)).last()
        if user is None:
            return None

        set_user_login_details(request, 'username', True)

        if not user.check_password(password):
            return None
        return user
