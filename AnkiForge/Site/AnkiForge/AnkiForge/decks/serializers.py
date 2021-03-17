from rest_framework import serializers
from django.conf import settings
from decks.models import IncomingCards, UserDecks
from membership.models import UserMembership

class UserDecksSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    class Meta():
        # Minimal fields means less for api electron to process
        fields = [
            'id', 'user','ankiforge_deck_name',
        ]
        model = UserDecks
        # fields = [
        #     'id', 'user', 'deck_id', 'ankiforge_deck_name', 'anki_deck_name',
        #     'native_lang', 'learnt_lang', 'images_enabled', 'audio_enabled',
        #     'model_code'
        # ]

class IncomingCardsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncomingCards
        fields = [
            'user', 'deck', 'cost', 'ready_for_archive', 'submitted_to_archive',
            'incoming_quote', 'quote_received_date', 'deck_made', 'archived_card'
        ]
        # Getting rid of error that user is reuired
        read_only_fields = ('user',)

class ReadyForForgeCardsSerializer(serializers.ModelSerializer):

    class Meta:
        model = IncomingCards
        fields = ['user', 'deck','incoming_quote']
        # Getting rid of error that user is reuired
        read_only_fields = ('user',)
    

class UserPointsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMembership
        fields = ['user', 'user_points']

        read_only_fields = ['user']



