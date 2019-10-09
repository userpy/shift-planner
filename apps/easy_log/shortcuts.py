import os

from django.utils.timezone import get_current_timezone
from apps.easy_log.settings import ACTIONS, LOG_DATETIME_FORMAT, LOG_SHORT_DATE_FORMAT, LOG_SHORT_DATETIME_FORMAT, SOURCE


def add_log(**kwargs):
    from datetime import datetime
    from apps.easy_log.models import LogJournal
    from apps.easy_log.settings import SOURCE

    data = kwargs.pop('value', {})

    params = {
        'created': kwargs.pop('created', datetime.now(get_current_timezone())),
        'process_id': os.getpid(),
        'is_atomic': kwargs.pop('is_atomic', True),
        'action': kwargs.pop('action'),
    }
    data.update({
        'source': kwargs.pop('source', SOURCE.TERMINAL),
        'source_info': kwargs.pop('source_info'),
    })

    # Если еще что-то осталось передано - сохраняем в data
    # перед этим удаляя то, что не может быть преобразовано в JSON
    if 'credentials' in kwargs:
        if 'strategy' in kwargs['credentials']:
            kwargs['credentials'].pop('strategy')
        if 'storage' in kwargs['credentials']:
            kwargs['credentials'].pop('storage')
        if 'backend' in kwargs['credentials']:
            kwargs['credentials'].pop('backend')
    data.update(kwargs)
    params['data'] = data

    return LogJournal.write_to_journal(**params)


# ------- AUTH SHORTCUTS ------------

def log_login(user_id,
              username,
              useragent,
              source_info,
              authmethod,
              source=SOURCE.PORTAL):
    """ LOGIN action shortcut """
    return add_log(user_id=user_id,
                   username=username,
                   useragent=useragent,
                   source_info=source_info,
                   action=ACTIONS.LOGIN,
                   source=source,
                   is_atomic=True,
                   authmethod=authmethod)


def log_login_fail(credentials,
                   reason,
                   user_was_found,
                   useragent,
                   source_info,
                   source=SOURCE.PORTAL):
    """ LOGIN_FAIL action shortcut """
    return add_log(source_info=source_info,
                   action=ACTIONS.LOGIN_FAIL,
                   source=source,
                   reason=reason,
                   credentials=credentials,
                   user_was_found=user_was_found,
                   useragent=useragent,
                   is_atomic=True)


def log_logout(user_id,
               username,
               useragent,
               source_info,
               source=SOURCE.PORTAL):
    """ LOGOUT action shortcut """
    return add_log(user_id=user_id,
                   username=username,
                   useragent=useragent,
                   source_info=source_info,
                   action=ACTIONS.LOGOUT,
                   source=source,
                   is_atomic=True)

# ------------- QUOTA VOLUME ---------------


def log_quota_volume_new(user_id,
                         entity_id,
                         headquarter,
                         organization,
                         source_info,
                         start,
                         end,
                         source=SOURCE.PORTAL,
                         **kwargs):
    """ QUOTA_VOLUME_NEW action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='QuotaVolume',
                   headquarter=headquarter,
                   aheadquarter=None,
                   organization=organization,
                   agency=None,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATE_FORMAT),
                   end=end.strftime(LOG_SHORT_DATE_FORMAT) if end else None,
                   action=ACTIONS.QUOTA_VOL_NEW,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_quota_volume_edit(user_id,
                          entity_id,
                          headquarter,
                          organization,
                          source_info,
                          start,
                          end,
                          source=SOURCE.PORTAL,
                          **kwargs):
    """ QUOTA_VOLUME_EDIT action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='QuotaVolume',
                   headquarter=headquarter,
                   aheadquarter=None,
                   organization=organization,
                   agency=None,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATE_FORMAT),
                   end=end.strftime(LOG_SHORT_DATE_FORMAT) if end else None,
                   action=ACTIONS.QUOTA_VOL_EDIT,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_quota_volume_del(user_id,
                         entity_id,
                         headquarter,
                         organization,
                         source_info,
                         start,
                         end,
                         source=SOURCE.PORTAL,
                         **kwargs):
    """ QUOTA_VOLUME_DEL action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='QuotaVolume',
                   headquarter=headquarter,
                   aheadquarter=None,
                   organization=organization,
                   agency=None,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATE_FORMAT),
                   end=end.strftime(LOG_SHORT_DATE_FORMAT) if end else None,
                   action=ACTIONS.QUOTA_VOL_DEL,
                   source=source,
                   is_atomic=True,
                   **kwargs)

# ------------- QUOTA ---------------


def log_quota_new(user_id,
                  entity_id,
                  headquarter,
                  promo,
                  organization,
                  source_info,
                  start,
                  end,
                  source=SOURCE.PORTAL,
                  **kwargs):
    """ QUOTA_NEW action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='Quota',
                   headquarter=headquarter,
                   aheadquarter=promo,
                   organization=organization,
                   agency=None,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATE_FORMAT),
                   end=end.strftime(LOG_SHORT_DATE_FORMAT) if end else None,
                   action=ACTIONS.QUOTA_NEW,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_quota_edit(user_id,
                   entity_id,
                   headquarter,
                   promo,
                   organization,
                   source_info,
                   start,
                   end,
                   source=SOURCE.PORTAL,
                   **kwargs):
    """ QUOTA_EDIT action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='Quota',
                   headquarter=headquarter,
                   aheadquarter=promo,
                   organization=organization,
                   agency=None,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATE_FORMAT),
                   end=end.strftime(LOG_SHORT_DATE_FORMAT) if end else None,
                   action=ACTIONS.QUOTA_EDIT,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_quota_del(user_id,
                  entity_id,
                  headquarter,
                  promo,
                  organization,
                  source_info,
                  start,
                  end,
                  source=SOURCE.PORTAL,
                  **kwargs):
    """ QUOTA_DEL action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='Quota',
                   headquarter=headquarter,
                   aheadquarter=promo,
                   organization=organization,
                   agency=None,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATE_FORMAT),
                   end=end.strftime(LOG_SHORT_DATE_FORMAT) if end else None,
                   action=ACTIONS.QUOTA_DEL,
                   source=source,
                   is_atomic=True,
                   **kwargs)

# ------------- PROMO SHIFT ---------------


def log_promo_shift_new(user_id,
                        entity_id,
                        headquarter,
                        promo,
                        organization,
                        agency,
                        source_info,
                        start,
                        end,
                        source=SOURCE.PORTAL,
                        **kwargs):
    """ PROMO_SHIFT_NEW action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='PromoShift',
                   headquarter=headquarter,
                   aheadquarter=promo,
                   organization=organization,
                   agency=agency,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATETIME_FORMAT),
                   end=end.strftime(LOG_SHORT_DATETIME_FORMAT),
                   action=ACTIONS.PROMO_SHIFT_NEW,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_promo_shift_edit(user_id,
                         entity_id,
                         headquarter,
                         promo,
                         organization,
                         agency,
                         source_info,
                         start,
                         end,
                         source=SOURCE.PORTAL,
                         **kwargs):
    """ PROMO_SHIFT_EDIT action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='PromoShift',
                   headquarter=headquarter,
                   aheadquarter=promo,
                   organization=organization,
                   agency=agency,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATETIME_FORMAT),
                   end=end.strftime(LOG_SHORT_DATETIME_FORMAT),
                   action=ACTIONS.PROMO_SHIFT_EDIT,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_promo_shift_del(user_id,
                        entity_id,
                        headquarter,
                        promo,
                        organization,
                        agency,
                        source_info,
                        start,
                        end,
                        source=SOURCE.PORTAL,
                        **kwargs):
    """ PROMO_SHIFT_DEL action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='PromoShift',
                   headquarter=headquarter,
                   aheadquarter=promo,
                   organization=organization,
                   agency=agency,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATETIME_FORMAT),
                   end=end.strftime(LOG_SHORT_DATETIME_FORMAT),
                   action=ACTIONS.PROMO_SHIFT_DEL,
                   source=source,
                   is_atomic=True,
                   **kwargs)

# ------------- OUTSOURCING SHIFT ---------------


def log_out_shift_new(user_id,
                      entity_id,
                      headquarter,
                      aheadquarter,
                      organization,
                      agency,
                      source_info,
                      start,
                      end,
                      source=SOURCE.PORTAL,
                      **kwargs):
    """ OUT_SHIFT_NEW action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='OutsourcingShift',
                   headquarter=headquarter,
                   aheadquarter=aheadquarter,
                   organization=organization,
                   agency=agency,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATETIME_FORMAT),
                   end=end.strftime(LOG_SHORT_DATETIME_FORMAT),
                   action=ACTIONS.OUT_SHIFT_NEW,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_out_shift_edit(user_id,
                       entity_id,
                       headquarter,
                       aheadquarter,
                       organization,
                       agency,
                       source_info,
                       start,
                       end,
                       source=SOURCE.PORTAL,
                       **kwargs):
    """ OUT_SHIFT_EDIT action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='OutsourcingShift',
                   headquarter=headquarter,
                   aheadquarter=aheadquarter,
                   organization=organization,
                   agency=agency,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATETIME_FORMAT),
                   end=end.strftime(LOG_SHORT_DATETIME_FORMAT),
                   action=ACTIONS.OUT_SHIFT_EDIT,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_out_shift_del(user_id,
                      entity_id,
                      headquarter,
                      aheadquarter,
                      organization,
                      agency,
                      source_info,
                      start,
                      end,
                      source=SOURCE.PORTAL,
                      **kwargs):
    """ OUT_SHIFT_DEL action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='OutsourcingShift',
                   headquarter=headquarter,
                   aheadquarter=aheadquarter,
                   organization=organization,
                   agency=agency,
                   source_info=source_info,
                   start=start.strftime(LOG_SHORT_DATETIME_FORMAT),
                   end=end.strftime(LOG_SHORT_DATETIME_FORMAT),
                   action=ACTIONS.OUT_SHIFT_DEL,
                   source=source,
                   is_atomic=True,
                   **kwargs)

# ------------- AVAILABILITY ---------------


def log_avail_new(user_id,
                  entity_id,
                  headquarter,
                  promo,
                  organization,
                  agency,
                  source_info,
                  start,
                  end,
                  source=SOURCE.PORTAL,
                  **kwargs):
    """ AVAIL_NEW action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='Availability',
                   headquarter=headquarter,
                   aheadquarter=promo,
                   organization=organization,
                   agency=agency,
                   source_info=source_info,
                   start=start.isoformat(),
                   end=end.isoformat(),
                   action=ACTIONS.AVAIL_NEW,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_avail_edit(user_id,
                   entity_id,
                   headquarter,
                   promo,
                   organization,
                   agency,
                   source_info,
                   start,
                   end,
                   source=SOURCE.PORTAL,
                   **kwargs):
    """ AVAIL_EDIT action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='Availability',
                   headquarter=headquarter,
                   aheadquarter=promo,
                   organization=organization,
                   agency=agency,
                   source_info=source_info,
                   start=start.isoformat(),
                   end=end.isoformat(),
                   action=ACTIONS.AVAIL_EDIT,
                   source=source,
                   is_atomic=True,
                   **kwargs)


def log_avail_del(user_id,
                  entity_id,
                  headquarter,
                  promo,
                  organization,
                  agency,
                  source_info,
                  start,
                  end,
                  source=SOURCE.PORTAL,
                  **kwargs):
    """ AVAIL_DEL action shortcut """
    return add_log(user_id=user_id,
                   entity_id=entity_id,
                   entity_class='Availability',
                   headquarter=headquarter,
                   aheadquarter=promo,
                   organization=organization,
                   agency=agency,
                   source_info=source_info,
                   start=start.isoformat(),
                   end=end.isoformat(),
                   action=ACTIONS.AVAIL_DEL,
                   source=source,
                   is_atomic=True,
                   **kwargs)
