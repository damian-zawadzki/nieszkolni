# Generated by Django 4.0.4 on 2023-01-31 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0045_client_wage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='wage',
            field=models.IntegerField(default=50),
        ),
    ]
