# Заполняет поля email, full_name для уведомлений созданных ранее

from django.db import migrations, models


def update_notify_items(apps, schema_editor):
    NotifyItem = apps.get_model('notifications', 'NotifyItem')
    for item in NotifyItem.objects.all():
        if item.user:
            item.full_name = f'{item.user.first_name} {item.user.last_name}'
            item.email = item.user.email
            item.save(update_fields=['email', 'full_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_auto_20180628_1318'),
        ('outsource', '0081_auto_20180628_1318'),
    ]

    operations = [
        migrations.RunPython(update_notify_items),
    ]