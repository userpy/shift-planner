# Generated by Django 2.0.5 on 2019-06-06 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0020_auto_20190508_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='promoshift',
            name='dt_change',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Последнее изменение'),
        ),
    ]
