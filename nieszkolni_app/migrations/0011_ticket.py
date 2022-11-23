# Generated by Django 4.0.4 on 2022-11-22 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0010_remove_set_sentence_id_set_sentence_ids_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stamp', models.IntegerField(default=0)),
                ('opening_date', models.IntegerField(default=0)),
                ('closing_date', models.IntegerField(default=0)),
                ('client', models.CharField(default='', max_length=200)),
                ('ticket_type', models.CharField(default='', max_length=200)),
                ('subject', models.CharField(default='', max_length=200)),
                ('description', models.TextField(default='')),
                ('reporting_user', models.CharField(default='', max_length=200)),
                ('responsible_user', models.CharField(default='', max_length=200)),
                ('status', models.CharField(default='', max_length=200)),
                ('importance', models.IntegerField(default=0)),
            ],
        ),
    ]
