from django.contrib import admin
from .models import UserMembership, Subscription, StripeSubscription, EmailList
# Register your models here.
admin.site.register(UserMembership)
admin.site.register(Subscription)
admin.site.register(StripeSubscription)
admin.site.register(EmailList)