# Generated by Django 3.1.3 on 2020-12-12 14:03

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0003_auto_20201212_1355'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='incomingcards',
            managers=[
                ('readyforprocess_objects', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='incomingcards',
            name='ready_for_archive',
            field=models.BooleanField(default=True),
        ),
    ]
