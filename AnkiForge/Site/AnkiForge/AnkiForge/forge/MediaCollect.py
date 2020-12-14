from google.cloud import translate_v2 as translate
import os
""" WHEN RUNNING THROUGH DOCKER UNCOMMENT THIS """

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/code/GoogleKey.json"

"""WHEN RUNNING TESTING UNCOMMENT THIS"""

# The taask will pass the data like this as a query set, which can be treated as a dictionary
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/GoogleKey.json"
quotes = [
            {
                'id': 2, 'user_id': 1, 'deck_id': 1,
                'deck__learnt_lang': 'es', 'deck__native_lang': 'en',
                'deck__images_enabled': True, 'deck__audio_enabled': True,
                'incoming_quote': 'You would deeply regret it if you lost it all'
            },
            {
                'id': 1, 'user_id': 1, 'deck_id': 1, 
                'deck__learnt_lang': 'es', 'deck__native_lang': 'en', 
                'deck__images_enabled': True, 'deck__audio_enabled': True, 
                'incoming_quote': 'This Is the quote for celery'
            }
        ]

Controller(quotes)

# To begin, take input text, detect lang, translate to target lang
class Controller():

    def __init__(self, quotes):
        print(quotes)
        for q in quotes:
            print()
        self.T = Translate(quotes)

class Translate():

    def __init__(self, quotes):
        self.translate_client = translate.Client()
    

