# Generated by Django 4.2.2 on 2024-07-18 03:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('opportunitiesDB', '0005_activeopps_deadlinestring'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activeopps',
            name='description',
            field=models.TextField(max_length=100000),
        ),
    ]
