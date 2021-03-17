from celery import shared_task
from membership.models import Subscription
from celery.decorators import task
from celery.utils.log import get_task_logger
import time
from AnkiForge.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
import datetime

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

@shared_task(name='subscription_payment_email')
def subsciption_payment_email(user_email, first_name, epoch_active_until):
    payment_date = datetime.datetime.utcfromtimestamp(epoch_active_until).strftime('%Y-%m-%d')
    cancel_url = 'www.google.com'
    first_name = first_name.capitalize()
    send_mail(
        'Thank you for subscribing to AnkiForge',
        f"""Hi {first_name}, 
        
This is just an email to confirm that your subscription payment has been received. You now have access to our automatic language card making service until {payment_date}. On this date you will be charged again. If you wish to cancel your membership please visit {cancel_url}.
        
Thank you for subscribing to Ankiforge, if you have any issues, please don't hesitate to get in touch using this email address.
""",
        EMAIL_HOST_USER,
        [user_email],
        fail_silently = False
    )


@shared_task(name='subscription_cancelled_email')
def subscription_cancelled_email(user_email, first_name, end_date):
    cancel_url = 'www.google.com'
    first_name = first_name.capitalize()
    send_mail(
        'AnkiForge Confirmation of Subscription Cancellation',
        f"""Hi {first_name}, 
        
I am sorry to hear you have decided to cancel your subscription to AnkiForge. However, I hope you found the service and useful it assisted you on your language learning journey! 

You're subscription has been cancelled and you won't be charged again, however you will still have access to AnkiForge up until {end_date}. If you want to start using the service again, you know where we are.
        
Thank you for your subscription to Ankiforge, if you have any issues or feedback, please don't hesitate to get in touch using this email address.

Kind regards,

Jordan
""",
        EMAIL_HOST_USER,
        [user_email],
        fail_silently = False
    )



