# Generated by Django 4.0.4 on 2022-06-21 08:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0036_rename_links_libraryline_link'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='libraryline',
            unique_together={('name', 'link')},
        ),
    ]
