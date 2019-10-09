from apps.easy_log.journal.processors.auth import AuthProcessor
from apps.easy_log.journal.processors.quotavolume import QuotaVolumeProcessor
from apps.easy_log.journal.processors.quota import QuotaProcessor
from apps.easy_log.journal.processors.promoshift import PromoShiftProcessor
from apps.easy_log.journal.processors.outshift import OutsourcingShiftProcessor
from apps.easy_log.journal.processors.availability import AvailabilityProcessor

all_processors = (
    AuthProcessor,
    QuotaVolumeProcessor,
    QuotaProcessor,
    PromoShiftProcessor,
    PromoShiftProcessor,
    OutsourcingShiftProcessor,
    AvailabilityProcessor
)
