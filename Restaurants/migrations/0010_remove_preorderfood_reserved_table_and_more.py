# Generated by Django 4.2.3 on 2023-08-07 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Restaurants', '0009_reservation_reservedtable_preorderfood'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preorderfood',
            name='reserved_table',
        ),
        migrations.AddField(
            model_name='preorderfood',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='preorderfood',
            name='reservation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Restaurants.reservation'),
        ),
    ]
