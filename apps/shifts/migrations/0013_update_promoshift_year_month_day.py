# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def update_promo_shifts(apps, schema_editor):
    PromoShift = apps.get_model("shifts", "PromoShift")
    for promo_shift in PromoShift.objects.all():
        promo_shift.year = promo_shift.start_date.year
        promo_shift.month = promo_shift.start_date.month
        promo_shift.day = promo_shift.start_date.day
        promo_shift.save(update_fields=['month', 'year', 'day'])

class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0012_auto_20181115_1408'),
    ]

    operations = [
        migrations.RunPython(update_promo_shifts),
    ]