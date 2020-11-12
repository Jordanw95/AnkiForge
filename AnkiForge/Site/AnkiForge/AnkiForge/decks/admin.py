from django.contrib import admin
from .models import CardModels, UserDecks, ArchivedCards, IncomingCards

admin.site.register(CardModels)
admin.site.register(UserDecks)
admin.site.register(ArchivedCards)
admin.site.register(IncomingCards)

# Register your models here.
