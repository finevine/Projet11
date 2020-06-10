# Generated by Django 3.0.7 on 2020-06-07 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_remove_category_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='slug',
            field=models.SlugField(editable=False, max_length=100, null=True, unique=True),
        ),
    ]