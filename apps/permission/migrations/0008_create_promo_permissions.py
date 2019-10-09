# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def create_default_permission(apps, schema_editor):
    Permission = apps.get_model("permission", "Permission")
    AccessRole = apps.get_model("permission", "AccessRole")
    Page = apps.get_model("permission", "Page")

    promo_role = AccessRole.objects.create(name='Роль промоутер', code='promo_default', party='promo')
    for page in Page.objects.filter(parent__isnull=True, party=promo_role.party):
        Permission.objects.create(page=page, role=promo_role, action='read')
        Permission.objects.create(page=page, role=promo_role, action='write')

class Migration(migrations.Migration):

    dependencies = [
        ('permission', '0007_convert_access_profiles'),
    ]

    operations = [
        migrations.RunPython(create_default_permission),
    ]