from celery import shared_task
from membership.models import Subscription
from celery.decorators import task
from celery.utils.log import get_task_logger
import time

logger = get_task_logger(__name__)


@shared_task(name='membership_check')
def membership_check():
    active_subscriptions = Subscription.active_subscriptions.all()
    current_time = time.time()
    for subscription in active_subscriptions:
        if subscription.active_until > current_time :
            print(f'User: {subscription.user_membership} is still active. They have {subscription.user_membership.user_points} points')
        else:
            subscription.active = False
            subscription.save()
            subscription.user_membership.user_points = 0
            subscription.user_membership.save()
            print(f'*** User: {subscription.user_membership} IS NO LONGER ACTIVE. It is now {subscription.active} that there subscription is active. They now have {subscription.user_membership.user_points} points***')

