# Generated by Django 4.0.4 on 2022-11-30 10:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0017_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stamp', models.IntegerField(default=0)),
                ('date_number', models.IntegerField(default=0)),
                ('clock_in', models.IntegerField(default=0)),
                ('clock_out', models.IntegerField(default=0)),
                ('duration', models.IntegerField(default=0)),
                ('category_number', models.IntegerField(default=0)),
                ('category_name', models.CharField(default='', max_length=200)),
                ('remarks', models.CharField(default='', max_length=200)),
                ('status', models.CharField(default='', max_length=200)),
                ('clocking_user', models.CharField(default='', max_length=200)),
                ('entry_type', models.CharField(default='', max_length=200)),
                ('value', models.IntegerField(default=0)),
                ('tag', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category_name', models.CharField(default='', max_length=200)),
                ('category_display_name', models.CharField(default='', max_length=200)),
                ('category_number', models.IntegerField(default=0)),
                ('value', models.IntegerField(default=0)),
            ],
        ),
    ]