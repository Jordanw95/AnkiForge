from celery import shared_task
from decks.models import IncomingCards, ArchivedCards, MediaTransactions
from celery.decorators import task
from celery.utils.log import get_task_logger
from forge.MediaCollect import Controller

logger = get_task_logger(__name__)

# Potentially change this to async task where can send query as argument (maybe even dict it first).
#  NEED TO LOOK INTO HOW THIS WILL WORK WITH MULTIPLE WORKERS
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
        print(processed.final_result)
        final_result = (processed.final_result)
    # translated_result = {'id': 185, 'user_id': 1, 'deck_id': 2, 'deck__learnt_lang': 'zh-TW', 'deck__native_lang': 'en', 'deck__images_enabled': True, 'deck__audio_enabled': True, 'incoming_quote': '你好', 'original_language': 'zh-CN', 'translated_language': 'en', 'translated_quote': 'Hello there'}
    # Check that translation worked
    if final_result:
        archived_object = make_archivedcards(final_result)                      # Make archived
        updated_quote = update_incomingcards(final_result, archived_object)    #Updated incoming card
        make_mediatransactions(final_result, updated_quote)    # Make transaction record~

        print("***TRANSLATION COMPLETE TASK COMPLETE***")
    else :
        print("***Failed to translate card***")

        

def make_archivedcards(final_result):
        archived_object = ArchivedCards(
            original_quote = final_result['incoming_quote'],
            original_language = final_result['original_language'],
            translated_quote = final_result['translated_quote'],
            translated_language = final_result['translated_language'],
            aws_audio_file_path = final_result['aws_audio_file_path'],
            aws_image_file_path= "",
            universal_filename= final_result['universal_filename'],
            upload_audio_success= final_result['upload_audio_success'],
            upload_image_success= False,
            voiced_quote= final_result['voiced_quote'],
            voiced_quote_lang= final_result['voiced_quote_lang'],
        )
        archived_object.save()
        return archived_object

def update_incomingcards(final_result, archived_object):
        updated_quote = IncomingCards.objects.get(id=final_result['id'])
        updated_quote.ready_for_archive = False
        updated_quote.submitted_to_archive=True
        updated_quote.archived_card = archived_object
        updated_quote.save()
        return updated_quote

def make_mediatransactions(final_result, updated_quote):
        transaction_object = MediaTransactions( 
            incoming_card = updated_quote,
            charecters_sent_translator = len(final_result['incoming_quote']),
            charecters_returned_translator = len(final_result['translated_quote']),
            charecters_sent_detect = len(final_result['detection_quote']),
            audio_enabled = final_result['deck__audio_enabled'],
            media_enabled =final_result['deck__images_enabled'],
            characters_sent_azure_voice= len(final_result['voiced_quote']),
            voiced_quote_lang=final_result['voiced_quote_lang'],
            found_in_archive=False,
        )
        transaction_object.save()