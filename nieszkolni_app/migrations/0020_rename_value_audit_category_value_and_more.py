# Generated by Django 4.0.4 on 2022-11-30 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0019_rename_tag_audit_tags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='audit',
            old_name='value',
            new_name='category_value',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='value',
            new_name='category_value',
        ),
    ]
