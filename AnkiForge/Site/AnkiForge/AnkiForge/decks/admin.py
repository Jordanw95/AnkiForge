from django.contrib import admin
from .models import CardModels, UserDecks, ArchivedCards, IncomingCards, MediaTransactions

admin.site.register(CardModels)
admin.site.register(UserDecks)
admin.site.register(ArchivedCards)
admin.site.register(IncomingCards)
admin.site.register(MediaTransactions)

# Register your models here.
