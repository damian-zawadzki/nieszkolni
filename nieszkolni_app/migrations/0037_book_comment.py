# Generated by Django 4.0.4 on 2023-01-15 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0036_alter_catalogue_catalogue_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='comment',
            field=models.CharField(default='', max_length=200),
        ),
    ]
