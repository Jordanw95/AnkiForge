from django.urls import path, include
from decks import views
# from django.contrib.auth import views as auth_views

app_name = "decks"

urlpatterns = [
    path('decks_preview/', views.DecksIndexView.as_view(), name='decks_preview'),
    path('createdeck/', views.UserDecksCreateView.as_view(), name='decks_create'),
    path('mydecks/', views.UserDecksList.as_view(), name = 'decks_list'),
    path('decks_preview/standard', views.DecksPreviewStandard.as_view(), name='decks_preview_standard'),
    path('decks_preview/stanard_tbs', views.DecksPreviewStandardTBS.as_view(), name='decks_preview_standard_tbs')
]
