# Generated by Django 4.0.4 on 2022-11-21 18:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0009_composer_item_composer_set_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='set',
            name='sentence_id',
        ),
        migrations.AddField(
            model_name='set',
            name='sentence_ids',
            field=models.CharField(default='', max_length=200),
        ),
        migrations.AlterField(
            model_name='set',
            name='set_id',
            field=models.IntegerField(default=0),
        ),
    ]
