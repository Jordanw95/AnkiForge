from celery import shared_task
from decks.models import IncomingCards, ArchivedCards
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
    
    for quote in quotes:   
        processed = Controller(quote)
        print(processed.translated_result)
        translated_result = (processed.translated_result)
    # translated_result = {'id': 185, 'user_id': 1, 'deck_id': 2, 'deck__learnt_lang': 'zh-TW', 'deck__native_lang': 'en', 'deck__images_enabled': True, 'deck__audio_enabled': True, 'incoming_quote': '你好', 'original_language': 'zh-CN', 'translated_language': 'en', 'translated_quote': 'Hello there'}
    # create archived object
    archived_object = ArchivedCards(
        original_quote = translated_result['incoming_quote'],
        original_language = translated_result['original_language'],
        translated_quote = translated_result['translated_quote'],
        translated_language = translated_result['translated_language'],
        audio_file_path = "",
        image_file_path= "",
    )
    archived_object.save()
    # update properties of incomingcards object
    new_quotes = IncomingCards.objects.get(id=new_item)
    new_quotes.ready_for_archive = False
    new_quotes.submitted_to_archive=True
    new_quotes.archived_card = archived_object
    new_quotes.save()
    print("***TRANSLATION COMPLETE TASK COMPLETE***")

        
