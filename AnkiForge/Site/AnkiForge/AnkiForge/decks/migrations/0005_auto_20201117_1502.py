# Generated by Django 3.1.3 on 2020-11-17 15:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0004_auto_20201117_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdecks',
            name='anki_deck_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='userdecks',
            name='ankiforge_deck_name',
            field=models.CharField(max_length=50),
        ),
    ]