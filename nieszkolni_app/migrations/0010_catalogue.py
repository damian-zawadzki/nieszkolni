# Generated by Django 4.0.4 on 2022-06-09 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0009_rename_entry_type_dictionary_deck'),
    ]

    operations = [
        migrations.CreateModel(
            name='Catalogue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entry', models.CharField(default='', max_length=200)),
                ('entry_number', models.IntegerField()),
                ('catalogue_number', models.IntegerField()),
                ('catalogue_name', models.CharField(default='', max_length=200)),
            ],
        ),
    ]
