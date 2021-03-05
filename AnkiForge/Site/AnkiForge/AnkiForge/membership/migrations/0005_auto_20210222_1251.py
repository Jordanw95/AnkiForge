# Generated by Django 3.1.3 on 2021-02-22 12:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('membership', '0004_auto_20210222_1048'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usermembership',
            name='stipe_customer_id',
        ),
        migrations.RemoveField(
            model_name='usermembership',
            name='stripe_subscription_id',
        ),
        migrations.CreateModel(
            name='StripeSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stipe_customer_id', models.CharField(max_length=255)),
                ('stripe_subscription_id', models.CharField(max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_stripe_subscription', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
