# Generated by Django 3.1.3 on 2021-02-02 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0018_auto_20210202_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdecks',
            name='native_lang',
            field=models.CharField(choices=[('en', 'English')], default='en', max_length=50),
        ),
    ]
