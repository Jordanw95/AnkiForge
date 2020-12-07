from rest_framework import serializers
from django.conf import settings
from decks.models import IncomingCards, UserDecks

class UserDecksSerializer(serializers.ModelSerializer):
    class Meta():
        model = UserDecks
        fields = [
            'user', 'deck_id', 'ankiforge_deck_name', 'anki_deck_name',
            'native_lang', 'learnt_lang', 'images_enabled', 'audio_enabled',
            'model_code'
        ]

class IncomingCardsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncomingCards
        fields = [
            'user', 'deck', 'cost', 'ready_for_archive', 'submitted_to_archive',
            'incoming_quote', 'quote_received_date', 'deck_made', 'archived_card'
        ]
        # Getting rid of error that user is reuired
        read_only_fields = ('user',)

    


# class SnippetSerializer(serializers.ModelSerializer):
#     owner = serializers.ReadOnlyField(source='owner.username')
#     class Meta:
#         model = Snippet
#         fields = ['id', 'title', 'code', 'linenos', 'language', 'style', 'owner']


# """Creating representations of users in the API"""
# class UserSerializer(serializers.ModelSerializer):
#     """Because 'snippets' is a reverse relationship on the User model, 
#     it will not be included by default when using the ModelSerializer class, so we needed to add an explicit field for it."""
#     snippets = serializers.PrimaryKeyRelatedField(many=True, queryset=Snippet.objects.all())

#     class Meta:
#         model = User
#         fields = ['id', 'username', 'snippets']


