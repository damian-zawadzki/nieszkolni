# Generated by Django 4.0.4 on 2022-11-15 15:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='maximal_interval',
            field=models.IntegerField(default=90, null=True),
        ),
    ]
