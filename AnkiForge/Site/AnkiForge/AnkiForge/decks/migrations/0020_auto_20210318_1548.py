# Generated by Django 3.1.3 on 2021-03-18 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0019_auto_20210202_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdecks',
            name='learnt_lang',
            field=models.CharField(choices=[('en', 'English'), ('es', 'Spanish'), ('ja', 'Japanese'), ('zh-CN', 'Chinese (Simplified)'), ('zh-TW', 'Chinese (Traditional)'), ('de', 'German'), ('it', 'Italian'), ('fr', 'French')], max_length=50),
        ),
    ]