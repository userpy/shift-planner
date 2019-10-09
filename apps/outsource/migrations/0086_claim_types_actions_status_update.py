# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_status_actions(apps, schema_editor):
    ClaimRequest = apps.get_model("outsource", "ClaimRequest")
    ClaimStatus = apps.get_model("outsource", "ClaimStatus")
    ClaimAction = apps.get_model("outsource", "ClaimAction")

    ClaimRequest.objects.all().update(status=None)
    ClaimStatus.objects.all().delete()
    ClaimAction.objects.all().delete()

    actions = [
        {'name': 'Принять',
         'code': 'accept',
         'sort_key': '1',
         'need_comment': False
         },
        {'name': 'Отклонить',
         'code': 'reject',
         'sort_key': '2',
         'need_comment': True
         },
        {'name': 'Закрыть',
         'code': 'close',
         'sort_key': '3',
         'need_comment': False
         },
        {'name': 'Открыть повторно',
         'code': 'reopen',
         'sort_key': '4',
         'need_comment': False
         }
    ]

    statuses = [
        {'name': 'На рассмотрении',
         'code': 'wait',
         'sort_key': '1',
         },
        {'name': 'Отклонена',
         'code': 'reject',
         'sort_key': '2',
         },
        {'name': 'В работе',
         'code': 'accept',
         'sort_key': '3',
         },
        {'name': 'Закрыта',
         'code': 'closed',
         'sort_key': '4',
         }
    ]

    for status in statuses:
        ClaimStatus.objects.create(**status)

    for action in actions:
        ClaimAction.objects.create(**action)


def update_statuses(apps, schema_editor):
    ClaimStatus = apps.get_model("outsource", "ClaimStatus")
    ClaimRequest = apps.get_model("outsource", "ClaimRequest")
    ClaimMessage = apps.get_model("outsource", "ClaimMessage")

    for claim in ClaimRequest.objects.all():
        if not claim.dt_closed:
            messages = ClaimMessage.objects.filter(claim=claim)
            if messages:
                status_code = 'accept'
                dt_state_transfer = messages.order_by('-dt_created').first().dt_created
            else:
                status_code = 'wait'
                dt_state_transfer = claim.dt_created
        else:
            status_code = 'closed'
            dt_state_transfer = claim.dt_closed
        status = ClaimStatus.objects.filter(code=status_code).first()
        claim.status = status
        claim.dt_closed = dt_state_transfer
        claim.save(update_fields=['status', 'dt_closed'])


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0085_auto_20180629_1118'),
    ]

    operations = [
        migrations.RunPython(create_status_actions),
        migrations.RunPython(update_statuses),
    ]