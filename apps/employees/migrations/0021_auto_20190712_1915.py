# Generated by Django 2.0.5 on 2019-07-12 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0020_orghistory_is_inactive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orghistory',
            name='is_inactive',
            field=models.BooleanField(verbose_name='Неактивен (проходит обучение)'),
        ),
    ]
