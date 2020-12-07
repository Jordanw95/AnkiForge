from django.urls import path, include
from decks import views
# from django.contrib.auth import views as auth_views

app_name = "decks"

urlpatterns = [
    path('index/', views.DecksIndexView.as_view(), name='decks_index'),
    path('createdeck/', views.UserDecksCreateView.as_view(), name='decks_create'),
    path('mydecks/', views.UserDecksList.as_view(), name = 'decks_list'),
]
