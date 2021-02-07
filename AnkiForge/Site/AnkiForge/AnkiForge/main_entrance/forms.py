from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from membership.models import Membership, UserMembership, Subscription

class MySignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')

    # Actual defined membership types 
    payg_membership = Membership.objects.get(membership_type='PAYG')
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self):
        user= super().save(commit=False)
        user.save()
        # Creating a new UserMembership
        user_membership = UserMembership.objects.create(user=user, membership=self.payg_membership, user_points = 1000)
        user_membership.save()
        # Creating the UserSubscription
        user_subscription = Subscription()
        user_subscription.user_membership = user_membership
        user_subscription.save()
        return user

    
