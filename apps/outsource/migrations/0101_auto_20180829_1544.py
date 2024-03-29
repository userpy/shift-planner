# Generated by Django 2.0.5 on 2018-08-29 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0100_auto_20180824_1718'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='outsource.Agency', verbose_name='Агентство'),
        ),
        migrations.AlterField(
            model_name='headquater',
            name='party',
            field=models.CharField(choices=[('client', 'Клиент'), ('agency', 'Агентство'), ('promo', 'Промоутер')], default='client', max_length=8, verbose_name='Тип'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='outsource.Organization', verbose_name='Город'),
        ),
    ]
