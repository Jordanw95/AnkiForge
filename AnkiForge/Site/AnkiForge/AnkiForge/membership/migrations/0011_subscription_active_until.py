# Generated by Django 3.1.3 on 2021-03-03 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0010_remove_subscription_active_until'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='active_until',
            field=models.PositiveIntegerField(default=0),
        ),
    ]