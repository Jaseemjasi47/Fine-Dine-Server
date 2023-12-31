# Generated by Django 4.2.3 on 2023-07-27 16:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Restaurants', '0004_alter_food_description_table'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='restaurants_owned', to=settings.AUTH_USER_MODEL),
        ),
    ]
