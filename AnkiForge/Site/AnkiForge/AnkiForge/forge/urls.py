from django.urls import path, include
from forge import views
# from django.contrib.auth import views as auth_views

app_name = "forge"

urlpatterns = [
    path('index/', views.ForgeIndexView.as_view(), name='forge_index'),
    path('add_card/', views.IncomingCardCreateView.as_view(), name = 'forge_add_incoming_card'),
]
