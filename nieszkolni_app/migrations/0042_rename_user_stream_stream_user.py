# Generated by Django 4.0.4 on 2022-09-21 11:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0041_submission_revision_date'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stream',
            old_name='user',
            new_name='stream_user',
        ),
    ]