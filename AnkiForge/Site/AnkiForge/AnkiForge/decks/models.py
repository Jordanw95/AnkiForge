from django.db import models
from django.conf import settings
from django.utils import timezone
import random
from django.urls import reverse

class CardModels(models.Model):
    CODE = 1041609445
    CARD_TYPE ='Basic (and reversed card)' 
    CSS="""
        .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color: white;
        }
        .media {
        margin: 2px;
        }
    """
    FIELDS=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'MyMedia'},
        {'name': 'MyAudio'}, 
    ]
    TEMPLATES=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}<br>{{MyMedia}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{MyAudio}}',
        }, 
        {
            'name': 'Card 3',
            'qfmt': '{{MyAudio}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{Question}}<br>{{MyMedia}}',
        },           
    ]

    model_name = models.CharField(max_length=50)
    anki_model_code = models.TextField(default={
                                'code' : CODE,
                                'card_type': CARD_TYPE,
                                'css' : CSS,
                                'fields' : FIELDS,
                                'templates' : TEMPLATES
                                })
    def __str__(self):
        return self.model_name
class UserDecks(models.Model):
    NATIVE_LANG_CHOICES = (
        ('en', 'English'),
        ('es', 'Spanish')
    )

    LEARNT_LANG_CHOICES = (
        ('en', 'English'),
        ('es', 'Spanish')
    )
        
    CODE = 1041609445
    CARD_TYPE ='Basic (and reversed card)' 
    CSS="""
        .card {
        font-family: arial;
        font-size: 20px;
        text-align: center;
        color: black;
        background-color: white;
        }
        .media {
        margin: 2px;
        }
    """
    FIELDS=[
        {'name': 'Question'},
        {'name': 'Answer'},
        {'name': 'MyMedia'},
        {'name': 'MyAudio'}, 
    ]
    TEMPLATES=[
        {
            'name': 'Card 1',
            'qfmt': '{{Question}}<br>{{MyMedia}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{MyAudio}}',
        }, 
        {
            'name': 'Card 3',
            'qfmt': '{{MyAudio}}',
            'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{Question}}<br>{{MyMedia}}',
        },           
    ]
    DEFAULT_MODEL={
        'code' : CODE,
        'card_type': CARD_TYPE,
        'css' : CSS,
        'fields' : FIELDS,
        'templates' : TEMPLATES
        }

    def make_random_number():
        return random.randint(1000000000, 9999999999)
    
    def get_absolute_url(self):
        return reverse("decks:decks_index")
    

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'user_decks', on_delete=models.CASCADE)
    deck_id = models.PositiveBigIntegerField(blank=True, default = make_random_number)
    ankiforge_deck_name = models.CharField(max_length=50)
    anki_deck_name = models.CharField(max_length=50)
    native_lang = models.CharField(
        choices = NATIVE_LANG_CHOICES, default = 'en',
        max_length = 50
    )
    learnt_lang = models.CharField(
        choices = LEARNT_LANG_CHOICES, default = 'es',
        max_length = 50
    )
    images_enabled = models.BooleanField(default= True)
    audio_enabled = models.BooleanField(default = True)
    model_code = models.ForeignKey(CardModels, related_name = 'model_code', on_delete=models.SET_DEFAULT,
    default=DEFAULT_MODEL)


    def __str__(self):
        return self.ankiforge_deck_name

class ArchivedCards(models.Model):
    original_quote = models.CharField(max_length=240)
    original_language = models.CharField(max_length=50)
    translated_quote = models.TextField(max_length=300)
    translated_language = models.CharField(max_length=50)
    audio_file_path = models.TextField(max_length=1000, default ="")
    image_file_path= models.TextField(max_length=1000, default ="")
    
    def __str__(self) :
        return self.original_quote


class IncomingCards(models.Model):
    
    # class ReadyForProcess(models.Manager):
    #     def get_queryset(self):
    #         return super().get_queryset().filter(ready_for_archive =True)

    def get_absolute_url(self):
        return reverse("forge:forge_index")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'user_cards', on_delete=models.CASCADE)
    deck = models.ForeignKey(UserDecks, related_name = 'target_deck', on_delete=models.CASCADE)
    cost = models.PositiveIntegerField(default = 5)
    ready_for_archive = models.BooleanField(default = False)
    submitted_to_archive = models.BooleanField(default = False)
    incoming_quote = models.CharField(max_length=200)
    quote_received_date = models.DateTimeField(default=timezone.now)
    deck_made =  models.BooleanField(default = False)
    archived_card = models.ForeignKey(ArchivedCards, related_name='archived_card', on_delete=models.CASCADE, blank = True, null=True)
    
    # Manager instances
    # readyforprocessobject = ReadyForProcess()

    # Charging

    def save(self, *args, **kwargs):
        quote_length = len(self.incoming_quote)
        user = self.user
        membership = user.user_membership
        deck = self.deck
        media_costs = 0
        translation_cost = quote_length * 1

        if deck.images_enabled:
            media_costs += 100
        if deck.audio_enabled:
            media_costs += quote_length * 1
        
        self.cost = media_costs + translation_cost
        resultant_balance = membership.user_points - self.cost

        if resultant_balance >= 0 :
            membership.user_points = resultant_balance
            self.ready_for_archive = True
            user.user_membership.save()
        else :
            raise Exception("Insufficient credit for this transaction")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"User: {self.user.username} Quote: '{self.incoming_quote}''"

# Create your models here.
