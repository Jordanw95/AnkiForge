from celery import shared_task
from decks.models import IncomingCards
from celery.decorators import task
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@shared_task
def translate_and_archive():
    quotes = IncomingCards.readyforprocess_objects.values()
    print(quotes)
        
