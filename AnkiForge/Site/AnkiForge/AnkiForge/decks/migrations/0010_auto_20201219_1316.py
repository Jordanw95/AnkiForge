# Generated by Django 3.1.3 on 2020-12-19 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0009_auto_20201219_1315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mediatransactions',
            name='charecters_sent_detect',
            field=models.IntegerField(),
        ),
    ]
