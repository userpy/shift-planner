from django.contrib.auth.models import User
from social_core.exceptions import AuthException
import uuid


def create_or_update_employee(backend, saml_superuser_ou, saml_update_user=False, saml_update_employee=False, user=None, **kwargs):

    default = kwargs.get('name_id', None)
    dn = kwargs.get('DN', None)

    # Если основные параметры не найдены
    # выходим
    if not default or not dn:
        return None

    # Получаем атрибуты из запроса
    username = kwargs.get('username', default)
    email = kwargs.get('EMail', None)

    if email:
        email = email[0]
    else:
        email = default

    first_name = kwargs.get('FirstName', None)
    if not first_name:
        message = 'Не передан параметр FirstName'
        raise AuthException(backend, message)
    else:
        first_name = first_name[0]

    last_name = kwargs.get('LastName', None)
    if not last_name:
        message = 'Не передан параметр LastName'
        raise AuthException(backend, message)
    else:
        last_name = last_name[0]

    # Берем первый OU из DN
    ou = dn[0].split(',OU=')[1].split(',OU=')[0]
    if ou == saml_superuser_ou:
        is_superuser = True
    else:
        is_superuser = False

    # Если сотрудника нет
    # то создаем
    if not user:
        # Создаем рандомный пароль
        password = str(uuid.uuid4())
        if is_superuser:
            user = User.objects.create_superuser(username=username,
                                                 email=email,
                                                 first_name=first_name,
                                                 last_name=last_name,
                                                 password=password)
        else:
            user = User.objects.create_user(username=username,
                                            email=email,
                                            first_name=first_name,
                                            last_name=last_name,
                                            password=password)
        return user
    # Если сотрудник есть
    # то обновляем
    else:
        if saml_update_user:
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.is_active = True
            if is_superuser:
                user.is_superuser = True
                user.is_staff = True
            else:
                user.is_superuser = False
                user.is_staff = False
            user.save()
        return user
