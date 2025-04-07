# Generated by Django 5.1.7 on 2025-04-06 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='account_type',
            field=models.CharField(choices=[('BUYER', 'BUYER'), ('SELLER', 'SELLER')], default='BUYER', max_length=6),
        ),
    ]
