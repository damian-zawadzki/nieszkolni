# Generated by Django 4.0.4 on 2022-11-02 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0075_quiz_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('quiz_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('client', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('collection_id', models.IntegerField(default=0)),
                ('question_id', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='quiz',
            name='quiz_question_id',
            field=models.IntegerField(default=0),
        ),
    ]