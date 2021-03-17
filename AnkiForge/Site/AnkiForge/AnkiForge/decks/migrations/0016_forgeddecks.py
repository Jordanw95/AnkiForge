# Generated by Django 3.1.3 on 2021-02-01 14:05

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0015_auto_20210123_1157'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForgedDecks',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aws_file_path', models.TextField(default=None, max_length=1000, null=True)),
                ('aws_download_link', models.TextField(default=None, max_length=1000, null=True)),
                ('local_file_path', models.TextField(default=None, max_length=1000, null=True)),
                ('deck_filename', models.TextField(default=None, max_length=1000, null=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('number_of_cards', models.IntegerField(default=0)),
                ('deck', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='forged_deck_deck', to='decks.userdecks')),
            ],
        ),
    ]
