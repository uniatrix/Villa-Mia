# Generated by Django 5.0.6 on 2024-07-26 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_room_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='available',
            field=models.BooleanField(default=True),
        ),
    ]