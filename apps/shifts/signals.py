from django.dispatch import Signal

promo_shift_change_signal = Signal(providing_args=['old_shift', 'new_shift'])
