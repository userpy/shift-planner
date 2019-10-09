from django.dispatch import Signal

edit_agency_employee_signal = Signal(providing_args=['old_agency_employee', 'new_agency_employee'])
