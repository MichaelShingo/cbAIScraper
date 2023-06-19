# Generated by Django 4.2.2 on 2023-06-19 07:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('opportunitiesDB', '0002_alter_activeopps_deadline'),
    ]

    operations = [
        migrations.AddField(
            model_name='activeopps',
            name='createdAt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='activeopps',
            name='websiteName',
            field=models.CharField(default='First Scrape', max_length=150),
            preserve_default=False,
        ),
    ]
