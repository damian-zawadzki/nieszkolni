# Generated by Django 4.0.4 on 2022-11-16 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0005_rename_daily_limit_of_new_cards_sentences_client_daily_limit_of_new_sentences_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='content_file',
            field=models.FileField(null=True, upload_to=''),
        ),
    ]