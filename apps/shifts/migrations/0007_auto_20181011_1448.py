# Generated by Django 2.0.5 on 2018-10-11 11:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outsource', '0107_auto_20181011_1448'),
        ('shifts', '0006_promoshift'),
    ]

    operations = [
        migrations.AddField(
            model_name='promoshift',
            name='duration',
            field=models.IntegerField(default=0, verbose_name='Продолжительность'),
        ),
        migrations.AddField(
            model_name='promoshift',
            name='store_area',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='outsource.StoreArea', verbose_name='КБГ'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='promoshift',
            name='aheadquarter',
            field=models.ForeignKey(blank=True, limit_choices_to={'party': 'promo'}, on_delete=django.db.models.deletion.PROTECT, related_name='aheadquarters', to='outsource.Headquater', verbose_name='Компания-промоутер'),
        ),
        migrations.AlterField(
            model_name='promoshift',
            name='headquarter',
            field=models.ForeignKey(blank=True, limit_choices_to={'party': 'client'}, on_delete=django.db.models.deletion.PROTECT, related_name='headquarters', to='outsource.Headquater', verbose_name='Клиент'),
        ),
        migrations.AlterField(
            model_name='promoshift',
            name='state',
            field=models.CharField(choices=[('accept', 'Подтверждена'), ('delete', 'Удалена')], default='accept', max_length=120, verbose_name='Состояние'),
        ),
        migrations.AlterField(
            model_name='promoshift',
            name='worktime',
            field=models.IntegerField(default=0, verbose_name='Рабочее время'),
        ),
    ]
