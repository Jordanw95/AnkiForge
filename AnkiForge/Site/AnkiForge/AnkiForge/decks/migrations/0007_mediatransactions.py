# Generated by Django 3.1.3 on 2020-12-17 13:57

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0006_auto_20201216_2145'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaTransactions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media_collected_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('charecters_sent_translator', models.IntegerField()),
                ('charecters_returned_translator', models.IntegerField()),
                ('audio_enabled', models.BooleanField(default=True)),
                ('media_enabled', models.BooleanField(default=True)),
                ('incoming_card', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='incoming_card', to='decks.incomingcards')),
            ],
        ),
    ]