# Generated by Django 5.0.6 on 2024-07-31 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_booking_is_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='new_reservation',
            field=models.BooleanField(default=True),
        ),
    ]