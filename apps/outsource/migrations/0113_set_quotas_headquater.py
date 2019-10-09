# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def set_quotas_headquarter(apps, schema_editor):
    Quota = apps.get_model("outsource", "Quota")
    for quota in Quota.objects.all():
        quota.headquarter = quota.store.headquater
        quota.save(update_fields=['headquarter'])

class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0112_auto_20181030_1212'),
    ]

    operations = [
        migrations.RunPython(set_quotas_headquarter),
    ]