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
    # Check that translation worked
    if final_result:
        if final_result['audio_found_in_db'] and final_result['image_found_in_db']:
            save_with_db_media(final_result)
            print(f"***INCOMING CARD SAVED WITH PREVIOUS ARCHIVED CARD ID = {final_result['archived_card_id']}***")
        else:
            save_with_retrieved_media(final_result)
    else :
        print("***FAILURE IN MEDIA_COLLECT.PY TO RETURN RESULT**")

def save_with_db_media(final_result):
    archived_object = ArchivedCards.objects.get(id = final_result['archived_card_id'])
    updated_quote = update_incomingcards(final_result, archived_object)
    make_mediatransactions(final_result, updated_quote)

def save_with_retrieved_media(final_result):    
    archived_object = make_archivedcards(final_result)                      # Make archived
    updated_quote = update_incomingcards(final_result, archived_object)    #Updated incoming card
    make_mediatransactions(final_result, updated_quote) 

def make_archivedcards(final_result):
        archived_object = ArchivedCards(
            original_quote = final_result['incoming_quote'],
            original_language = final_result['original_language'],
            translated_quote = final_result['translated_quote'],
            translated_language = final_result['translated_language'],
        )
        if final_result['deck__audio_enabled']:
            archived_object.aws_audio_file_path = final_result['aws_audio_file_path']
            archived_object.local_audio_file_path = final_result['local_file_path']
            archived_object.universal_audio_filename= final_result['universal_audio_filename']
            archived_object.upload_audio_success= final_result['upload_audio_success']
            archived_object.voiced_quote= final_result['voiced_quote']
            archived_object.voiced_quote_lang= final_result['voiced_quote_lang']
        if final_result['deck__images_enabled']:
            archived_object.aws_image_file_path=final_result['aws_image_file_path']
            archived_object.local_image_file_path = final_result['local_image_filepath']
            archived_object.universal_image_filename=final_result['universal_image_filename']
            archived_object.upload_image_success=final_result['upload_image_success']
            archived_object.image_search_phrase_string=final_result['image_search_phrase_string']
            archived_object.retrieved_image_url= final_result['retrieved_image_url']
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
        )
        if final_result['deck__audio_enabled']:
            transaction_object.voiced_quote_lang=final_result['voiced_quote_lang']
            transaction_object.audio_found_in_db=final_result['audio_found_in_db']
            if final_result['audio_found_in_db']:
                pass
            else: 
                transaction_object.characters_sent_azure_voice= len(final_result['voiced_quote'])
        if final_result['deck__images_enabled']:
            transaction_object.image_found_in_db=final_result['image_found_in_db']
        transaction_object.save()

# def make_mediatransaction_found_in_db(final_result, updated_quote, archived_object):
#         transaction_object = MediaTransactions( 
#             incoming_card = updated_quote,
#             charecters_sent_translator = len(final_result['incoming_quote']),
#             charecters_returned_translator = len(final_result['translated_quote']),
#             charecters_sent_detect = len(final_result['detection_quote']),
#             audio_enabled = final_result['deck__audio_enabled'],
#             media_enabled =final_result['deck__images_enabled'],
#         )
#         if final_result['deck__audio_enabled']:
#             transaction_object.voiced_quote_lang=final_result['voiced_quote_lang']
#             transaction_object.audio_found_in_db=final_result['audio_found_in_db']
#             transaction_object.characters_sent_azure_voice= len(final_result['voiced_quote'])
#         if final_result['deck__images_enabled']:
#             transaction_object.image_found_in_db=final_result['image_found_in_db']
#         transaction_object.save()