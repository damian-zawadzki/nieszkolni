# Generated by Django 4.0.4 on 2022-10-19 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0056_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='stamp',
            field=models.IntegerField(default=0),
        ),
    ]