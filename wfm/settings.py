"""
Copyright 2018 ООО «Верме»

Настройки проекта outsourcing
"""

import os
import logging
import tempfile
from .settings_local import DEBUG

from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i@g+(1qc06b@8ee4*3!f0i9g*28ddsx39gv!nvs9w_(p$)p*cy'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']  # TODO

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',

    'apps.outsource',
    'apps.claims',
    'apps.shifts',
    'apps.employees',
    'apps.remotes',
    'apps.notifications',
    'apps.lib',
    'apps.permission',
    'apps.config',
    'apps.authutils',
    'apps.violations',
    'apps.easy_log',

    'compressor',
    'social_django',
    'axes',

    'saml',
    'applogs',
    'xlsexport',
    'wfm_admin',
    'rangefilter',
]

AUTHENTICATION_BACKENDS = (
    #'django.contrib.auth.backends.ModelBackend',
    'apps.authutils.backends.EmailLoginBackend',
    'apps.authutils.backends.UsernameLoginBackend',
    'saml.backends.SAMLAuthExt',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # WARN: http://breachattack.com/, http://breachattack.com/resources/BREACH%20-%20SSL,%20gone%20in%2030%20seconds.pdf
    'django.middleware.gzip.GZipMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
)

ROOT_URLCONF = 'wfm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wfm.wsgi.application'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('WFM_DB_HOST', '127.0.0.1'),
        'NAME': os.environ.get('WFM_DB_NAME', 'out_db'),
        'USER': os.environ.get('WFM_DB_USER', 'wfm'),
        'PASSWORD': os.environ.get('WFM_DB_PASSWORD', 'wfm'),
    },
    'userlogs': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('WFM_DB_HOST', '127.0.0.1'),
        'NAME': 'wfm_log',
        'USER': os.environ.get('WFM_DB_USER', 'wfm'),
        'PASSWORD': os.environ.get('WFM_DB_PASSWORD', 'wfm'),
    },
    'applogs': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'HOST': os.environ.get('WFM_DB_HOST', '127.0.0.1'),
        'NAME': 'app_logs',
        'USER': os.environ.get('WFM_DB_USER', 'wfm'),
        'PASSWORD': os.environ.get('WFM_DB_PASSWORD', 'wfm'),
    },
}

try:
    from .settings_local import DATABASES
except ImportError:
    pass

DATABASE_ROUTERS = [
    'applogs.db_router.LogsDBRouter',
    'apps.easy_log.db_router.EasyLogRouter',
    'wfm.default_db_router.DefaultDBRouter',
]

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static_collected/")

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)

MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = '/upload/'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'compressor-cache': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(tempfile.gettempdir(), 'django_compressor_cache'),
        'TIMEOUT': None,
        'OPTIONS': {
            'MAX_ENTRIES': 1000,
        },
    },
    'axes_cache': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

try:
    from .settings_local import CACHES
except ImportError:
    pass

COMPRESS_CACHE_BACKEND = 'compressor-cache'
COMPRESS_ENABLED = False

try:
    from .settings_local import COMPRESS_ENABLED
except ImportError:
    pass

LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = LOGIN_URL

# -------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------- АВТОРИЗАЦИЯ ---------------------------------------------------------
# -------------------------------------------------------------------------------------------------------------------------

# Social Auth (social_core/pipeline/__init__.py)
# Доступные способы авторизации
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'saml.pipelines.associate_by_name_id',
    'social_core.pipeline.social_auth.associate_user',
)

# SAML error handler - ошибка авторизации
SOCIAL_AUTH_LOGIN_ERROR_URL = '/saml/error?type=login-error'
# SAML error handler - блокированный пользователь
SOCIAL_AUTH_INACTIVE_USER_URL = '/saml/error?type=inactive-user'
# SAML error handler - обрыв подключения
#SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = LOGOUT_REDIRECT_URL

# Информация о приложении
SOCIAL_AUTH_SAML_ORG_INFO = {
    "en-US": {
        "name": "Verme Identity Provider",
        "displayname": "Verme Identity Provider",
        "url": "https://verme.ru",
    }
}

# Контакты технического специалиста.
SOCIAL_AUTH_SAML_TECHNICAL_CONTACT = {
    "givenName": "VERME Info",
    "emailAddress": "info@verme.ru"
}

# Контакты поддержки
SOCIAL_AUTH_SAML_SUPPORT_CONTACT = {
    "givenName": "VERME Support",
    "emailAddress": "support@verme.ru",
}

# Общие параметры SAML-протокола
SOCIAL_AUTH_SAML_SECURITY_CONFIG = {
    'wantNameId': True,
    'wantAttributeStatement': False,
    "logoutRequestSigned": True,
    "logoutResponseSigned": True,
    "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
}


SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

try:
    from .social import *
except ImportError:
    pass

# Логи
class F(logging.Filter):
    """ Этот "фильтр" не фильтрует, а добавляет в объекты record айпи и имя
        юзера, делающего запрос, чтоб форматтер их вставил потом в строку """
    def filter(self, record):
        # TODO: похоже, это всё больше не работает, потому что вместо request'а тут какой-то socket
        request = getattr(record, 'request', None)

        if request and hasattr(request, 'user'):  # user
            record.user = request.user
        else:
            record.user = '--'

        if request and hasattr(request, 'META'):  # IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                record.ip = x_forwarded_for.split(',')[-1]
            else:
                record.ip = request.META.get('REMOTE_ADDR')
        else:
            record.ip = '--'

        return True

try:
    os.mkdir(os.path.join(BASE_DIR, 'logs'))
except FileExistsError:
    pass

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {
        'main': {
            '()': F
        }
    },
    'formatters': {
        'stamp': {
            'format': '%(levelname)s [%(asctime)s] %(ip)s "%(user)s" %(name)s.%(module)s %(message)s'
        },
    },
    'handlers': {
        'file_main': {
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'main.log'),
            'formatter': 'stamp',
            'filters': ['main'],
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'stamp',
            'filters': ['main'],
        },
        'db': {
            'class': 'applogs.handlers.DBLogsHandler',
            'filters': ['main'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file_main', 'console'],
            'level': 'WARNING',
        },
        'apps': {
            'handlers': ['file_main', 'console'],
            'level': 'DEBUG',
        },
        'command': {
            'handlers': ['db', 'console'],
            'level': 'DEBUG',
        },
        'api': {
            'handlers': ['db', 'console'],
            'level': 'DEBUG',
        },
        'remote_service': {
            'handlers': ['db', 'console'],
            'level': 'DEBUG',
        },
    },
}

try:
    from .wfm_admin import ADMIN_COLUMNS, ADMIN_SECTIONS
except ImportError:
    ADMIN_SECTIONS = {}
    ADMIN_COLUMNS = []

DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 10 MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000


# AXES config


def username_getter(request, credentials):
    from apps.authutils.views import axes_username_getter
    return axes_username_getter(request, credentials)


AXES_CACHE = 'axes_cache'
AXES_COOLOFF_TIME = timedelta(minutes=5)
AXES_FAILURE_LIMIT = 10
AXES_LOCKOUT_TEMPLATE = 'login_locked.html'
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
AXES_USERNAME_CALLABLE = username_getter
AXES_META_PRECEDENCE_ORDER = ('HTTP_X_REAL_IP',)

