# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def set_head(apps, schema_editor):
    Organization = apps.get_model("outsource", "Organization")
    head_org = Organization.objects.filter(kind='head', code='mvideo').first()
    for org in Organization.objects.filter(kind='city', parent__isnull=True):
        org.parent = head_org
        org.save()

class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0124_auto_20190206_1633'),
    ]

    operations = [
        migrations.RunPython(set_head),
    ]