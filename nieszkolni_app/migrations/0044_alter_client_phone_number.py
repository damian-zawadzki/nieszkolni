# Generated by Django 4.0.4 on 2022-09-21 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0043_alter_client_phone_number_alter_client_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='phone_number',
            field=models.IntegerField(default=987654321),
        ),
    ]
