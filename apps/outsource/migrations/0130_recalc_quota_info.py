# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from apps.shifts.methods import get_or_create_quota_info

def set_quotainfo(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0129_quotainfo'),
        ('shifts', '0015_promoshift_quota_info'),
    ]

    operations = [
        migrations.RunPython(set_quotainfo),
    ]