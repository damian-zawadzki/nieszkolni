# Generated by Django 4.0.4 on 2022-06-21 08:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0035_libraryline'),
    ]

    operations = [
        migrations.RenameField(
            model_name='libraryline',
            old_name='links',
            new_name='link',
        ),
    ]
