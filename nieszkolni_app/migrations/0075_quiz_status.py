# Generated by Django 4.0.4 on 2022-11-01 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0074_rename_test_id_quiz_quiz_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='status',
            field=models.CharField(default='', max_length=200),
        ),
    ]
