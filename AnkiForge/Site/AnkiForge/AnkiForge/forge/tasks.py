from celery import shared_task
from decks.models import IncomingCards
from celery.decorators import task
from celery.utils.log import get_task_logger
from forge.MediaCollect import Controller

logger = get_task_logger(__name__)

# Potentially change this to async task where can send query as argument (maybe even dict it first).
@shared_task
def translate_and_archive():
    quotes = list(IncomingCards.readyforprocess_objects.values(
        'id','user_id','deck_id','deck__learnt_lang',
        'deck__native_lang','deck__images_enabled',
        'deck__audio_enabled','incoming_quote'
        ))
    Controller(quotes)
    print("***TASK COMPLETE***")
        
