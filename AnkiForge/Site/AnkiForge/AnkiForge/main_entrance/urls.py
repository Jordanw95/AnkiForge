from django.urls import path, include
from main_entrance import views
# from django.contrib.auth import views as auth_views

app_name = "main_entrance"

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('account/login/', views.MyLoginView.as_view(), name = 'login'),
    path('account/logout/', views.MyLogoutView.as_view(), name = 'logout'),
    # path('account/signup/', views.mysignupview, name='signup'),
    path('howitworks/', views.HowItWorksView.as_view(), name='howitworks'),
    path('api/auth/login', views.APILoginView.as_view(), name='api_login'),
    path('api/auth/logout', views.APILogoutView.as_view(), name ='api_logout'),
]
