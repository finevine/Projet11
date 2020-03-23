# Generated by Django 3.0.4 on 2020-03-22 09:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=30)),
                ('name', models.CharField(max_length=100, null=True)),
                ('slug', models.SlugField(blank=True, max_length=100, null=True, unique=True)),
                ('nutritionGrade', models.CharField(max_length=1, null=True)),
                ('image', models.URLField(null=True)),
                ('fat', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Fat in 100g')),
                ('satFat', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Saturated fat in 100g')),
                ('sugar', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Sugar in 100g')),
                ('salt', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Salt in 100g')),
            ],
        ),
        migrations.CreateModel(
            name='ProductCategories',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Category name')),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='compared_to_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.ProductCategories'),
        ),
        migrations.CreateModel(
            name='Favourite',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codeHealthy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='healthy', to='products.Product')),
                ('codeUnhealthy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unhealthy', to='products.Product')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
