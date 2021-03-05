from django.db import models
from django.conf import settings
# Create your models here.
# MEMBERSHIP_CHOICES = (
# (‘Premium’, ‘pre’),
# (‘Free’, ‘free’)
# )

# The first element in each tuple is the actual value to be set on the model, 
# and the second element is the human-readable name. For example:

class UserMembership(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='user_membership', on_delete=models.CASCADE)
    user_points = models.PositiveIntegerField(default = 100)

    def __str__(self):
       return self.user.username


# Here later is where renewals etc. can be handled.
class ActiveSubscriptionsSearch(models.Manager):    
    def get_queryset(self):
        return super().get_queryset().filter(active = True)
        
class Subscription(models.Model):

    user_membership = models.OneToOneField(UserMembership, related_name='subscription', on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    active_until = models.PositiveIntegerField(default = 0) 
    # managers
    objects = models.Manager()
    active_subscriptions = ActiveSubscriptionsSearch()

    def __str__(self):
      return self.user_membership.user.username

class StripeSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='user_stripe_subscription', on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=255)
    stripe_subscription_id = models.CharField(max_length=255)




    