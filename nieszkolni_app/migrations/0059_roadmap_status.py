# Generated by Django 4.0.4 on 2022-10-24 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0058_remove_roadmap_examiner_1_attempt_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='roadmap',
            name='status',
            field=models.CharField(default='', max_length=200),
        ),
    ]