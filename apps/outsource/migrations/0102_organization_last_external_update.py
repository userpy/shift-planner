# Generated by Django 2.0.5 on 2018-08-30 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0101_auto_20180829_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='last_external_update',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Последнее обновление через API'),
        ),
    ]
