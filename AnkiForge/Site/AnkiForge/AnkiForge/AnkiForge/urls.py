"""AnkiForge URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from membership.models import Membership

""" Url Views for initial start, pre DB entry"""
# This checks if models have been migrated and data ha been input yet, and prevents
# running of views that rely on model instances or relationships. This
# allows Docker to build the container ready to run with no migrations
# try :
#     Membership.objects.filter(membership_type="PAYG").first()
#     urlpatterns = [
#         path('admin/', admin.site.urls),
#         path('', include('main_entrance.urls')),
#         path('membership/', include('membership.urls')),
#         path('decks/', include('decks.urls')),
#         path('forge/', include('forge.urls')),
#     ]
# except Exception as e :
#     urlpatterns = [
#         path('admin/', admin.site.urls),
#     ] 

FIRST_LAUNCH = False

if FIRST_LAUNCH:
        urlpatterns = [
        path('admin/', admin.site.urls),
    ]
else:
    urlpatterns = [
        path('admin/', admin.site.urls),
        path('', include('main_entrance.urls')),
        path('membership/', include('membership.urls')),
        path('decks/', include('decks.urls')),
        path('forge/', include('forge.urls')),
    ]