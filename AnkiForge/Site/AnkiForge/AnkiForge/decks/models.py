from django.db import models
from django.conf import settings
from django.utils import timezone
import random
from django.urls import reverse
# from forge.tasks import translate_and_archive
import celery
from django.db import transaction


class CardModels(models.Model):
    model_name = models.CharField(max_length=50)
    def __str__(self):
        return self.model_name

class UserDecks(models.Model):
    NATIVE_LANG_CHOICES = (
        ('en', 'English'),
        # ('es', 'Spanish'),
        # ('ja', 'Japanese'),
        # ('zh-CN', 'Chinese (Simplified)'),
        # ('zh-TW', 'Chinese (Traditional)'),
        # ('de', 'German'),
        # ('it', 'Italian'),
        # ('fr', 'French'),
    )

    LEARNT_LANG_CHOICES = (
        ('en', 'English'),
        ('es', 'Spanish'),
        ('ja', 'Japanese'),
        ('zh-CN', 'Chinese (Simplified)'),
        ('zh-TW', 'Chinese (Traditional)'),
        ('de', 'German'),
        ('it', 'Italian'),
        ('fr', 'French'),
    )
        
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
    model_code = models.ForeignKey(CardModels, related_name = 'model_code', on_delete=models.SET_NULL, blank = True, null = True)


    def __str__(self):
        return self.ankiforge_deck_name
    
class DuplicateArchiveSearch(models.Manager):    
    def get_queryset(self):
        return super().get_queryset().filter(upload_audio_success=True, upload_image_success=True)

# Dynamically make search manager

class ArchivedCards(models.Model):
    original_quote = models.CharField(max_length=240)
    original_language = models.CharField(max_length=50)
    translated_quote = models.TextField(max_length=300)
    translated_language = models.CharField(max_length=50)
    local_audio_file_path = models.TextField(max_length=1000, default =None, null = True)
    local_image_file_path = models.TextField(max_length=1000, default =None, null = True)
    aws_audio_file_path = models.TextField(max_length=1000, default =None, null = True)
    aws_image_file_path= models.TextField(max_length=1000, default =None, null = True)
    universal_audio_filename=models.TextField(max_length=1000, default =None, null=True)
    universal_image_filename=models.TextField(max_length=1000, default =None, null=True)
    upload_audio_success=models.BooleanField(default = False)
    upload_image_success=models.BooleanField(default = False)
    voiced_quote= models.TextField(max_length=1000, default =None, null=True)
    voiced_quote_lang=models.CharField(max_length=10, default=None, null=True)
    image_search_phrase_string= models.TextField(max_length=1000, default =None, null=True)
    retrieved_image_url= models.TextField(max_length=1000, default =None, null=True)

    # managers
    objects = models.Manager()
    duplicate_archive_search_objects = DuplicateArchiveSearch()
    
    def __str__(self) :
        return self.original_quote


""" GET QUOTES READY FOR PROCESSING """
class ReadyForProcess(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(ready_for_archive =True, submitted_to_archive = False)

class ForgedDecks(models.Model):
    aws_file_path = models.TextField(max_length=1000, default =None, null = True)
    aws_download_link = models.TextField(max_length=1000, default =None, null = True)
    local_file_path = models.TextField(max_length=1000, default =None, null = True)
    deck_filename = models.TextField(max_length=1000, default =None, null = True)
    date_created = models.DateTimeField(default=timezone.now)
    deck = models.ForeignKey(UserDecks, related_name = 'forged_deck_deck', on_delete=models.CASCADE)
    number_of_cards = models.IntegerField(default = 0)

    def __str__(self):
        return self.deck_filename

"""GET QUOTES READY FOR FORGE"""
class ReadyForForge(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            submitted_to_archive=True, 
            deck_made=False
        )
class IncomingCards(models.Model):
    

    def get_absolute_url(self):
        return reverse("forge:forge_index")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name = 'user_cards', on_delete=models.CASCADE)
    deck = models.ForeignKey(UserDecks, related_name = 'target_deck', on_delete=models.CASCADE)
    cost = models.PositiveIntegerField(default = 5)
    ready_for_archive = models.BooleanField(default = True)
    submitted_to_archive = models.BooleanField(default = False)
    incoming_quote = models.CharField(max_length=200)
    quote_received_date = models.DateTimeField(default=timezone.now)
    deck_made =  models.BooleanField(default = False)
    archived_card = models.ForeignKey(ArchivedCards, related_name='archived_card', on_delete=models.CASCADE, blank = True, null=True)
    forged_deck = models.ForeignKey(ForgedDecks, related_name='forged_deck', on_delete=models.SET_NULL, blank = True, null=True)
    
    # Manager instances
    objects = models.Manager()
    readyforprocess_objects = ReadyForProcess()
    readyforforge = ReadyForForge()

    # Charging based on users 300000
    def calc_cost(self):
        quote_length = len(self.incoming_quote)
        user = self.user
        membership = user.user_membership
        deck = self.deck
        media_costs = 0
        # Translation cost
        translation_cost = quote_length * 1.461

        if deck.images_enabled:
            media_costs += 520
        if deck.audio_enabled:
            media_costs += quote_length * 1.192
        
        self.cost = media_costs + translation_cost
        # Inlcuding s3 cost
        resultant_balance = membership.user_points - self.cost + 4

        if resultant_balance >= 0 :
            membership.user_points = resultant_balance
            self.ready_for_archive = True
            user.user_membership.save()
        else :
            raise Exception("Insufficient credit for this transaction")        

    def save(self, *args, **kwargs):
        if self.submitted_to_archive:
            super().save(*args, **kwargs)    
        else:
            self.calc_cost()
            print("***USER CHARED***")
            super().save(*args, **kwargs)
            # Firstly we need to use trasaction on commit to prevent data race
            #  Next we need to call task through send task to avoid circular import
            transaction.on_commit(lambda: celery.current_app.send_task('translate_and_archive', (self.id,)))
        
    def __str__(self):
        return f"User: {self.user.username} Quote: '{self.incoming_quote}''"

class MediaTransactions(models.Model):
    media_collected_date = models.DateTimeField(default=timezone.now)    
    incoming_card = models.OneToOneField(IncomingCards, related_name='incoming_card', on_delete=models.SET_NULL, null = True)
    charecters_sent_translator = models.IntegerField()
    charecters_returned_translator = models.IntegerField()
    charecters_sent_detect = models.IntegerField()
    audio_enabled = models.BooleanField(default = True)
    media_enabled = models.BooleanField(default = True)
    characters_sent_azure_voice=models.IntegerField(default=0)
    voiced_quote_lang=models.CharField(max_length=10)
    audio_found_in_db=models.BooleanField(default = False)
    image_found_in_db=models.BooleanField(default = False)

    def __str__(self):
        if self.audio_enabled:
            audio = 'with'
        else: 
            audio = 'without'
        if self.media_enabled:
            media = 'with'
        else: 
            media = 'without'
        return f"On {self.media_collected_date}, {self.charecters_sent_translator} were sent fortranslation {audio} audio and {media} pictures "
    


# Create your models here.
