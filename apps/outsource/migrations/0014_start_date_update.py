# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def set_start_date(apps, schema_editor):
    OutsourcingShift = apps.get_model("outsource", "OutsourcingShift")
    for shift in OutsourcingShift.objects.all():
        shift.start_date = shift.start
        shift.save()

class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0013_auto_20180221_1617'),
    ]

    operations = [
        migrations.RunPython(set_start_date),
    ]
