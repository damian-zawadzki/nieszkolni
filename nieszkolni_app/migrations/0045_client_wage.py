# Generated by Django 4.0.4 on 2023-01-31 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0044_surveyquestion_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='wage',
            field=models.IntegerField(default=0),
        ),
    ]
