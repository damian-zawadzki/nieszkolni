# Generated by Django 4.0.4 on 2023-02-07 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0047_order_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='reference',
            field=models.IntegerField(default=0),
        ),
    ]
