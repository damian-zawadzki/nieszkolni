# Generated by Django 4.0.4 on 2022-11-22 12:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0011_ticket'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='assigned_user',
            field=models.CharField(default='', max_length=200),
        ),
    ]