from apps.easy_log.presenters.login import LoginPresenter
from apps.easy_log.presenters.logout import LogoutPresenter
from apps.easy_log.presenters.login_fail import LoginFailPresenter
from apps.easy_log.presenters.quota import QuotaNewPresenter, QuotaEditPresenter, QuotaDelPresenter
from apps.easy_log.presenters.quotavolume import QuotaVolumeNewPresenter, QuotaVolumeEditPresenter, QuotaVolumeDelPresenter
from apps.easy_log.presenters.promoshift import PromoShiftNewPresenter, PromoShiftEditPresenter, PromoShiftDelPresenter
from apps.easy_log.presenters.outshift import OutShiftNewPresenter, OutShiftEditPresenter, OutShiftDelPresenter
from apps.easy_log.presenters.availability import AvailabilityNewPresenter, AvailabilityEditPresenter, AvailabilityDelPresenter



def get_presenter_class_factory(action):
    presenters = (
        LoginPresenter,
        LogoutPresenter,
        LoginFailPresenter,
        QuotaNewPresenter,
        QuotaEditPresenter,
        QuotaDelPresenter,
        QuotaVolumeNewPresenter,
        QuotaVolumeEditPresenter,
        QuotaVolumeDelPresenter,
        PromoShiftNewPresenter,
        PromoShiftEditPresenter,
        PromoShiftDelPresenter,
        OutShiftNewPresenter,
        OutShiftEditPresenter,
        OutShiftDelPresenter,
        AvailabilityNewPresenter,
        AvailabilityEditPresenter,
        AvailabilityDelPresenter,
    )

    presenters_dict = dict((cls.action, cls) for cls in presenters)
    return presenters_dict.get(action)
