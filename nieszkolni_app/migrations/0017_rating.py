# Generated by Django 4.0.4 on 2022-11-26 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0016_assessment_item_alter_composer_submission_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_number', models.IntegerField(default=0)),
                ('client', models.CharField(default='', max_length=200)),
                ('position', models.CharField(default='', max_length=200)),
                ('rating', models.IntegerField(default=0)),
            ],
        ),
    ]