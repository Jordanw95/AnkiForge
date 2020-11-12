from django.db import models
from django.conf import settings
from django.utils import timezone

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


    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'user_decks', on_delete=models.CASCADE)
    deck_id = models.PositiveBigIntegerField(blank=True)
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

class ArchivedCards(models.Model):
    original_quote = models.CharField(max_length=240)
    original_language = models.CharField(max_length=50)
    translated_quote = models.TextField(max_length=300)
    translated_language = models.CharField(max_length=50)
    audio_file_path = models.TextField(max_length=1000, default ="")
    image_file_path= models.TextField(max_length=1000, default ="")
    


class IncomingCards(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'user_cards', on_delete=models.CASCADE)
    deck = models.ForeignKey(UserDecks, related_name = 'target_deck', on_delete=models.CASCADE)
    cost = models.PositiveIntegerField()
    ready_for_archive = models.BooleanField(default = False)
    submitted_to_archive = models.BooleanField(default = False)
    incoming_quote = models.CharField(max_length=200)
    quote_received_date = models.DateTimeField(default=timezone.now)
    deck_made =  models.BooleanField(default = False)
    archived_card = models.ForeignKey(ArchivedCards, related_name='archived_card', on_delete=models.CASCADE, blank = True, null=True)



# Create your models here.
