# Generated by Django 2.0.5 on 2019-01-10 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('violations', '0003_auto_20181229_1522'),
    ]

    operations = [
        migrations.AlterField(
            model_name='violationrule',
            name='party',
            field=models.CharField(choices=[('client', 'Клиент'), ('agency', 'Агентство'), ('promo', 'Промоутер'), ('broker', 'Кредитный брокер')], default='client', max_length=8, verbose_name='Сторона'),
        ),
    ]
