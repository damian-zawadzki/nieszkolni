# Generated by Django 4.0.4 on 2022-06-13 11:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0020_alter_curriculum_completion_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='curriculum',
            name='submitting_user',
            field=models.CharField(default='', max_length=200),
        ),
    ]
