from django.urls import path, include
from membership import views
# from django.contrib.auth import views as auth_views

app_name = "membership"

urlpatterns = [
    path('select/', views.MembershipView.as_view(), name='select_membership'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
]
