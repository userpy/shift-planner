# Generated by Django 2.0.5 on 2018-10-31 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0011_auto_20181023_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='doctype',
            name='code',
            field=models.CharField(choices=[('medical', 'Мед. книжка'), ('other', 'Другой')], default='medical', max_length=250, verbose_name='Код'),
        ),
    ]
