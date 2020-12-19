from celery import shared_task
from decks.models import IncomingCards, ArchivedCards, MediaTransactions
from celery.decorators import task
from celery.utils.log import get_task_logger
from forge.MediaCollect import Controller

logger = get_task_logger(__name__)

# Potentially change this to async task where can send query as argument (maybe even dict it first).
@shared_task(name='translate_and_archive')
def translate_and_archive(new_item):
    quotes = IncomingCards.readyforprocess_objects.filter(id=new_item).values(
        'id','user_id','deck_id','deck__learnt_lang',
        'deck__native_lang','deck__images_enabled',
        'deck__audio_enabled','incoming_quote'
        )
    
    translated_result = False
    for quote in quotes:   
        processed = Controller(quote)
        print(processed.translated_result)
        translated_result = (processed.translated_result)
    # translated_result = {'id': 185, 'user_id': 1, 'deck_id': 2, 'deck__learnt_lang': 'zh-TW', 'deck__native_lang': 'en', 'deck__images_enabled': True, 'deck__audio_enabled': True, 'incoming_quote': '你好', 'original_language': 'zh-CN', 'translated_language': 'en', 'translated_quote': 'Hello there'}
    # Check that translation worked
    if translated_result:
        archived_object = make_archivedcards(translated_result)                      # Make archived
        updated_quote = update_incomingcards(translated_result, archived_object)    #Updated incoming card
        make_mediatransactions(translated_result, updated_quote)    # Make transaction record~

        print("***TRANSLATION COMPLETE TASK COMPLETE***")
    else :
        print("***Failed to translate card***")

        

def make_archivedcards(translated_result):
        archived_object = ArchivedCards(
            original_quote = translated_result['incoming_quote'],
            original_language = translated_result['original_language'],
            translated_quote = translated_result['translated_quote'],
            translated_language = translated_result['translated_language'],
            audio_file_path = "",
            image_file_path= "",
        )
        archived_object.save()
        return archived_object

def update_incomingcards(translated_result, archived_object):
        updated_quote = IncomingCards.objects.get(id=translated_result['id'])
        updated_quote.ready_for_archive = False
        updated_quote.submitted_to_archive=True
        updated_quote.archived_card = archived_object
        updated_quote.save()
        return updated_quote

def make_mediatransactions(translated_result, updated_quote):
        transaction_object = MediaTransactions( 
            incoming_card = updated_quote,
            charecters_sent_translator = len(translated_result['incoming_quote']),
            charecters_returned_translator = len(translated_result['translated_quote']),
            charecters_sent_detect = len(translated_result['detection_quote']),
            audio_enabled = translated_result['deck__audio_enabled'],
            media_enabled =translated_result['deck__images_enabled'],
        )
        transaction_object.save()