# Generated by Django 3.1.3 on 2020-12-19 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0007_mediatransactions'),
    ]

    operations = [
        migrations.AddField(
            model_name='mediatransactions',
            name='charecters_sent_detect',
            field=models.IntegerField(null=True),
        ),
    ]
