from django.core.management.base import BaseCommand
from apps.shifts.models import OutsourcingShift
from apps.notifications.methods import make_notify_data

class Command(BaseCommand):
    help = 'Add notification -->>'
    def handle(self, *args, **options):
        print('Тестирование : /admin/notifications/notifyitem')
        out_shift = OutsourcingShift.objects.exclude(state='delete').first()
        print(out_shift.guid, out_shift.state)
        make_notify_data(out_shift, 'agency', 'delete_shift_template')
        # Меняем состояние на удалена
        out_shift.state = 'delete'
        out_shift.save(update_fields=['state'])
