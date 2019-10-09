# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def create_default_permission(apps, schema_editor):
    Permission = apps.get_model("permission", "Permission")
    AccessRole = apps.get_model("permission", "AccessRole")
    Page = apps.get_model("permission", "Page")

    AccessRole.objects.create(name='Роль агентства', code='agency_default', party='agency')
    AccessRole.objects.create(name='Роль клиента', code='client_default', party='client')
    # TODO Добавить приязку страниц к основным,
    # иначе пермишены будут созданы для всех страниц
    for role in AccessRole.objects.all():
        for page in Page.objects.filter(parent__isnull=True, party=role.party):
            Permission.objects.create(page=page, role=role, action='read')
            Permission.objects.create(page=page, role=role, action='write')

class Migration(migrations.Migration):

    dependencies = [
        ('permission', '0005_auto_20180821_1720'),
    ]

    operations = [
        migrations.RunPython(create_default_permission),
    ]