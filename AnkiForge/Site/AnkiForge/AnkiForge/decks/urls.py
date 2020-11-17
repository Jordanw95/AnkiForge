from django.urls import path, include
from decks import views
# from django.contrib.auth import views as auth_views

app_name = "decks"

urlpatterns = [
    path('index/', views.DecksIndexView.as_view(), name='decks_index'),
    path('createdeck/', views.UserDeckCreateView.as_view(), name='decks_create'),
]
