# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from transliterate import translit

def bind_agency_to_headquater(apps, schema_editor):
    Agency = apps.get_model("outsource", "Agency")
    Headquater = apps.get_model("outsource", "Headquater")
    for agency in Agency.objects.all():
        name = agency.name
        splitted = name.split('-')

        headquater_name = splitted[0]
        code = translit(headquater_name, "ru", reversed=True).lower()

        headquater, created = Headquater.objects.get_or_create(name=headquater_name, code=code, party='agency')
        agency.headquater = headquater
        agency.save(update_fields=['headquater'])

class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0095_agency_headquater'),
    ]

    operations = [
        migrations.RunPython(bind_agency_to_headquater),
    ]