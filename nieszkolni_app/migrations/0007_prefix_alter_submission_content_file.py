# Generated by Django 4.0.4 on 2022-11-18 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0006_submission_content_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='Prefix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matrix', models.CharField(default='', max_length=200)),
                ('id_prefix', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='submission',
            name='content_file',
            field=models.FileField(null=True, upload_to='static/files'),
        ),
    ]
