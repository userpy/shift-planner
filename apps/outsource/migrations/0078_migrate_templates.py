# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_config_templates(apps, schema_editor):
    Headquater = apps.get_model("outsource", "Headquater")
    Config = apps.get_model("outsource", "Config")
    for headquater in Headquater.objects.all():
        if headquater.wait_req_template:
            Config.objects.update_or_create(headquater_id=headquater.id, key='wait_req_template', defaults={'value': headquater.wait_req_template})
        if headquater.accept_req_template:
            Config.objects.update_or_create(headquater_id=headquater.id, key='accept_req_template', defaults={'value': headquater.accept_req_template})
        if headquater.delete_shift_template:
            Config.objects.update_or_create(headquater_id=headquater.id, key='delete_shift_template', defaults={'value': headquater.delete_shift_template})

class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0077_auto_20180608_1521'),
    ]

    operations = [
        migrations.RunPython(create_config_templates),
    ]