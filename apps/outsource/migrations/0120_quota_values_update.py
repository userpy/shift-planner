# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def set_quotas_values(apps, schema_editor):
    Quota = apps.get_model("outsource", "Quota")
    for quota in Quota.objects.all():
        quota.value_ext = quota.value
        quota.value = 0
        quota.save(update_fields=['value', 'value_ext'])

class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0119_headquater_short'),
    ]

    operations = [
        migrations.RunPython(set_quotas_values),
    ]