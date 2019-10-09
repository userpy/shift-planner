from django.core.management.base import BaseCommand
from apps.employees.models import AgencyHistory, AgencyEmployee

class Command(BaseCommand):
    help = 'Updates files info from docs'

    def handle(self, *args, **options):
        for employee in AgencyEmployee.objects.filter(dismissal__isnull=True):
            eh = employee.ae_history.order_by('-start').first()
            if eh:
                eh.end = None
                eh.save()
