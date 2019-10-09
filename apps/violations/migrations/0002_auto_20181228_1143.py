# Generated by Django 2.0.5 on 2018-12-28 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('violations', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='violationrule',
            name='party',
            field=models.CharField(choices=[('client', 'Клиент'), ('agency', 'Агентство'), ('promo', 'Промоутер')], default='client', max_length=8, verbose_name='Сторона'),
        ),
    ]
