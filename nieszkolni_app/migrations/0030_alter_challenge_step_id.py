# Generated by Django 4.0.4 on 2022-12-28 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0029_challenge_step_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='step_id',
            field=models.IntegerField(default=0),
        ),
    ]
