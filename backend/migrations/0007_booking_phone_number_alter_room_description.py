# Generated by Django 5.0.6 on 2024-07-30 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0006_booking_guest_name_alter_booking_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.CharField(max_length=600),
        ),
    ]