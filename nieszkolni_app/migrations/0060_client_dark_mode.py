# Generated by Django 4.0.4 on 2023-02-16 13:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0059_pronunciation_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='dark_mode',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
