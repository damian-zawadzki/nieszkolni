# Generated by Django 4.0.4 on 2023-02-07 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nieszkolni_app', '0048_product_reference'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.URLField(default='https://media.istockphoto.com/id/1147521090/photo/empty-white-studio-room-abstract-background.jpg?b=1&s=170667a&w=0&k=20&c=qIL0XrSQi0fjnzyd1QsrtOCUdBmHvU8AhCwr_cxmofg='),
        ),
    ]