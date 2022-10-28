# Generated by Django 4.0.4 on 2022-10-27 08:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0063_module'),
    ]

    operations = [
        migrations.CreateModel(
            name='Matrix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matrix', models.CharField(default='', max_length=200)),
                ('limit_number', models.IntegerField()),
                ('component_id', models.CharField(default='', max_length=200)),
                ('component_type', models.CharField(default='', max_length=200)),
                ('assignment_type', models.CharField(default='', max_length=200)),
                ('title', models.CharField(default='', max_length=200)),
                ('content', models.TextField(default='')),
                ('resources', models.TextField(default='')),
                ('conditions', models.TextField(default='')),
            ],
        ),
        migrations.RemoveField(
            model_name='module',
            name='limit_number',
        ),
        migrations.RemoveField(
            model_name='module',
            name='matrix',
        ),
    ]
