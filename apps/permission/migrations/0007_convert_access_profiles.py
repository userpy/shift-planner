# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from apps.lib.utils import content_type_ids_for_models


def convert_access_profiles(apps, schema_editor):
    from apps.outsource.models import Agency, Organization
    from apps.permission.models import AccessRole
    AccessProfile = apps.get_model("outsource", "AccessProfile")

    base_client_org = None

    for accp in AccessProfile.objects.all():
        if accp.headquater:
            organization, created = Organization.objects.get_or_create(name=accp.headquater.name,
                                                                       code=accp.headquater.code,
                                                                       kind='head',
                                                                       headquater_id=accp.headquater.id)
            role = AccessRole.objects.filter(code='client_default').first()
            unit_type_id = content_type_ids_for_models(Organization)
            unit_id = organization.id
            headquater_id = accp.headquater.id
            base_client_org = organization
        else:
            role = AccessRole.objects.filter(code='agency_default').first()
            unit_type_id = content_type_ids_for_models(Agency)
            unit_id = accp.agency.id
            headquater_id = accp.agency.headquater.id
        create_new(accp.user, role, headquater_id, unit_type_id, unit_id)
    bind_organizations_to_head_organization(base_client_org)

def create_new(user, role, headquater_id, unit_type_id, unit_id):
    from apps.permission.models import AccessProfile
    AccessProfile.objects.create(user_id=user.id, role=role, headquater_id=headquater_id, unit_type_id=unit_type_id[0],
                                 unit_id=unit_id)

def bind_organizations_to_head_organization(base):
    if not base:
        return
    from apps.outsource.models import Organization
    for org in Organization.objects.filter(parent__isnull=True, headquater_id=base.headquater.id).exclude(id=base.id):
        org.parent_id = base.id
        org.save(update_fields=['parent_id'])



class Migration(migrations.Migration):

    dependencies = [
        ('permission', '0006_create_default_permission'),
        ('outsource', '0097_auto_20180822_1213'),
    ]

    operations = [
        migrations.RunPython(convert_access_profiles),
    ]