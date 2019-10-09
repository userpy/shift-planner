# coding=utf-8;

from apps.lib.utils import enum
from django.conf import settings

LOG_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S:%f'
LOG_SHORT_DATETIME_FORMAT = '%Y-%m-%d %H:%M'
LOG_SHORT_DATE_FORMAT = '%Y-%m-%d'

EASY_LOG = getattr(settings, 'EASY_LOG', {})

# Заполняем конфиги данными по-умолчанию (при необходимости)
EASY_LOG.update({
    'DB_ALIAS': EASY_LOG.get('DB_ALIAS', 'userlogs'),
    'RUN_FILE': EASY_LOG.get('RUN_FILE', '/tmp/easy_log.pid'),
    'FILENAME': EASY_LOG.get('FILENAME', 'easy_log'),
    'READER': EASY_LOG.get('READER', 'DB'),
    'RUN_UNIQUE': EASY_LOG.get('RUN_UNIQUE', True),
    'ROWS_PER_ACTION': EASY_LOG.get('ROWS_PER_ACTION', 20),
    'MAX_EXPORT_ROWS': 20000,
    'MAX_DESCRIPTION_PREVIEW_LENGTH': 500,
})


JOURNAL_STATUS = enum(
    NEW=1,
    WAIT_FOR_COMMIT=2,
    FAIL=3,
)

ACTIONS = enum(
    LOGIN=1,
    LOGIN_FAIL=2,
    LOGOUT=3,

    QUOTA_VOL_NEW=4,
    QUOTA_VOL_EDIT=5,
    QUOTA_VOL_DEL=6,

    QUOTA_NEW=7,
    QUOTA_EDIT=8,
    QUOTA_DEL=9,

    PROMO_SHIFT_NEW=10,
    PROMO_SHIFT_EDIT=11,
    PROMO_SHIFT_DEL=12,

    OUT_SHIFT_NEW=13,
    OUT_SHIFT_EDIT=14,
    OUT_SHIFT_DEL=15,

    AVAIL_NEW=16,
    AVAIL_EDIT=17,
    AVAIL_DEL=18,
)

SOURCE = enum(
    PORTAL=1,
    DJANGO=2,
    EXTERNAL=3,
    TERMINAL=4,
)

ACTION_CHOICES = (
    (ACTIONS.LOGIN, 'Авторизация'),
    (ACTIONS.LOGIN_FAIL, 'Ошибка авторизации'),
    (ACTIONS.LOGOUT, 'Выход из системы'),

    (ACTIONS.QUOTA_VOL_NEW, 'Ограничение квот: создание'),
    (ACTIONS.QUOTA_VOL_EDIT, 'Ограничение квот: редактирование'),
    (ACTIONS.QUOTA_VOL_DEL, 'Ограничение квот: удаление'),

    (ACTIONS.QUOTA_NEW, 'Квота: создание'),
    (ACTIONS.QUOTA_EDIT, 'Квота: редактирование'),
    (ACTIONS.QUOTA_DEL, 'Квота: удаление'),

    (ACTIONS.PROMO_SHIFT_NEW, 'Смена промоутера: создание'),
    (ACTIONS.PROMO_SHIFT_EDIT, 'Смена промоутера: редактирование'),
    (ACTIONS.PROMO_SHIFT_DEL, 'Смена промоутера: удаление'),

    (ACTIONS.OUT_SHIFT_NEW, 'Смена аутсорсера: создание'),
    (ACTIONS.OUT_SHIFT_EDIT, 'Смена аутсорсера: редактирование'),
    (ACTIONS.OUT_SHIFT_DEL, 'Смена аутсорсера: удаление'),

    (ACTIONS.AVAIL_NEW, 'Доступность: создание'),
    (ACTIONS.AVAIL_EDIT, 'Доступность: редактирование'),
    (ACTIONS.AVAIL_DEL, 'Доступность: удаление'),

)

SOURCE_CHOICES = (
    (SOURCE.PORTAL, 'Веб-интерфейс'),
    (SOURCE.DJANGO, 'Интерфейс администратора'),
    (SOURCE.EXTERNAL, 'Внешняя система'),
    (SOURCE.TERMINAL, 'Терминальные утилиты'),
)
