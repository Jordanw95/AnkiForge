# Generated by Django 3.1.3 on 2021-03-03 15:23

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0008_auto_20210303_1102'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='active_until',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]