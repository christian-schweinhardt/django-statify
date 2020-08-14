# Generated by Django 3.0.8 on 2020-08-14 07:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('statify', '0002_auto_20200814_0856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='url',
            name='url',
            field=models.CharField(max_length=255, unique=True, validators=[django.core.validators.RegexValidator('(^\\/[A-Za-z0-9\\-\\_\\%\\?\\&\\=]+)')], verbose_name='URL'),
        ),
    ]
