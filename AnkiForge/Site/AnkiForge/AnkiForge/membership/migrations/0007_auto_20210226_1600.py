# Generated by Django 3.1.3 on 2021-02-26 16:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('membership', '0006_auto_20210226_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='user_membership',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='subscription', to='membership.usermembership'),
        ),
    ]