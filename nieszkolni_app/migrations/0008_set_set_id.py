# Generated by Django 4.0.4 on 2022-11-18 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0007_prefix_alter_submission_content_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='set',
            name='set_id',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
