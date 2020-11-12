from django.db import models
from django.conf import settings
# Create your models here.
# MEMBERSHIP_CHOICES = (
# (‘Premium’, ‘pre’),
# (‘Free’, ‘free’)
# )

# The first element in each tuple is the actual value to be set on the model, 
# and the second element is the human-readable name. For example:
class Membership(models.Model):
    
    MEMBERSHIP_CHOICES = (
        ('PAYG', 'Pay As You Go'),
        ('T1', 'Tier One'),
        ('T2', 'Tier Two'),
        ('T3', 'Tier Three')
    )

    slug = models.SlugField(null=True, blank=True)
    membership_type = models.CharField(
    choices=MEMBERSHIP_CHOICES, default='PAYG',
    max_length=30
      )
    price = models.DecimalField(default=0, max_digits=5, decimal_places = 2)
    points_awarded = models.IntegerField()

    def __str__(self):
      return self.membership_type

class UserMembership(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='user_membership', on_delete=models.CASCADE)
    membership = models.ForeignKey(Membership, related_name='user_membership', on_delete=models.SET_NULL, null=True)
    user_points = models.PositiveIntegerField(default = 0)

    def __str__(self):
       return self.user.username


# Here later is where renewals etc. can be handled.
class Subscription(models.Model):

    user_membership = models.ForeignKey(UserMembership, related_name='subscription', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
      return self.user_membership.user.username


    