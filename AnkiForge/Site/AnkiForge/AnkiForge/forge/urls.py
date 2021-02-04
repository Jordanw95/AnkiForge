from django.urls import path, include
from forge import views
# from django.contrib.auth import views as auth_views

app_name = "forge"

urlpatterns = [
    path('index/', views.ForgeIndexView.as_view(), name='forge_index'),
    path('add_card/', views.IncomingCardCreateView.as_view(), name = 'forge_add_incoming_card'),
    path('api/userdecks/', views.UserDecksAPIList.as_view(), name='api_user_decks'),
    path('api/usercards/', views.UserIncomingCardsAPIList.as_view(), name = 'api_user_cards'),
    # path('forgedecks', views.ForgeDecks.as_view(), name = 'forge_forge_decks'),
    path('forgedecks/', views.ForgeDecksIndex.as_view(), name = 'forge_forge_decks_index'),
    path('forgedecks/<int:pk>/', views.ForgeDecksList.as_view(), name='forge_forge_decks'),
    path('forgedecks/<int:pk>/forge/', views.forge_action, name = 'forge_forge_action'),
    path('myforgeddecks/', views.AlreadyForgedDecksIndex.as_view(), name = 'forge_already_forged_index'),
    path('myforgeddecks/<int:pk>/', views.AlreadyForgedDecksList.as_view(), name = 'forge_already_forged_list'),
    path('myforgeddecks/download/<int:pk>', views.get_download, name = 'forge_already_forged_download')
]
