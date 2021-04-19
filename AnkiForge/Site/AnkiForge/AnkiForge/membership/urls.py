from django.urls import path, include
from membership import views
# from django.contrib.auth import views as auth_views

app_name = "membership"

urlpatterns = [
    path('profile/', views.user_profile_view, name='user_profile'),
    path('subscribe/', views.SubscribeView.as_view(), name='subscribe'),
    path('config/', views.strip_config, name='stripe_config'),
    path('create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('subscribe_success/', views.SubscribeSuccessView.as_view(), name = 'subscribe_success'),
    path('subscribe_cancel/', views.SubscribeCancelView.as_view(), name='subscribe_cancel'),
    path('email_notification/', views.EmailListFormView.as_view(), name = 'email_notification'),
    path('email_notification_success', views.EmailListSuccess.as_view(), name = 'email_list_success'),
    path('new_subscription_webhook/', views.stripe_webhook, name='new_subscription_webhook'),
    path('cancel_subscription/', views.cancel_subscription, name = 'cancel_subscription'),
    path('out_of_points/', views.out_of_points, name ='out_of_points'),
]
