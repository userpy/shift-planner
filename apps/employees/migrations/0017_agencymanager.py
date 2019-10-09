# Generated by Django 2.0.5 on 2019-06-10 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0016_auto_20190520_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgencyManager',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=1000, verbose_name='ФИО')),
                ('position', models.CharField(blank=True, max_length=100, verbose_name='Должность')),
                ('phone', models.CharField(blank=True, max_length=12, verbose_name='Телефон')),
                ('email', models.EmailField(blank=True, max_length=100, verbose_name='EMail')),
            ],
            options={
                'verbose_name': 'Менеджер агентства',
                'verbose_name_plural': 'Менеджеры агентств',
                'ordering': ['-id'],
            },
        ),
    ]
