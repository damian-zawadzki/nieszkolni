# Generated by Django 4.0.4 on 2022-11-21 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0008_set_set_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='composer',
            name='item',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='composer',
            name='set_id',
            field=models.IntegerField(default=0),
        ),
    ]