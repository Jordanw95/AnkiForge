from google.cloud import translate_v2 as translate
import os
import six
""" WHEN RUNNING THROUGH DOCKER UNCOMMENT THIS """

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/code/GoogleKey.json"

"""WHEN RUNNING TESTING UNCOMMENT THIS"""

# The taask will pass the data like this as a query set, which can be treated as a dictionary
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/jordanwaters/Desktop/Python/GitHubRepositories/AnkiForge/AnkiForge/Site/AnkiForge/AnkiForge/GoogleKey.json"


# To begin, take input text, detect lang, translate to target lang
class Controller():

    def __init__(self, quotes):
        # At this point we are handed quotes with a 
        self.quotes = quotes

        # Here we translate the quote
        self.T = Translate(self.quotes)
        self.translated_result = self.T.translation_result
        # print(self.translated_result)

        # here is the resultant dictionary we will return
        self.result = self.quotes



class Translate():

    def __init__(self, quotes):
        self.translate_client = translate.Client()
        self.translation_result = self.make_translation(quotes, 'es')
        

    def make_translation(self, quotes, target):
        for quote in quotes:
            result = self.translate_client.translate(quote['incoming_quote'], target_language=target)
            quote['translated_quote'] = result['translatedText']
            quote['translated_language']= target        
        return quotes
        # ready_quotes = [quote['incoming_quote'] for quote in quotes]
        # results = self.translate_client.translate(ready_quotes, target_language=target)
        # for quote, result in zip(quotes, results):
        #     quote['translated_quote'] = result['translatedText']
        #     quote['translated_language']= target
        # return quotes 


"""WHEN RUNNING TESTING UNCOMMENT THIS"""

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
            },
            {
                'id': 1, 'user_id': 1, 'deck_id': 1, 
                'deck__learnt_lang': 'es', 'deck__native_lang': 'en', 
                'deck__images_enabled': True, 'deck__audio_enabled': True, 
                'incoming_quote': 'This Is another the quote for celery'
            },
            {
                'id': 1, 'user_id': 1, 'deck_id': 1, 
                'deck__learnt_lang': 'es', 'deck__native_lang': 'en', 
                'deck__images_enabled': True, 'deck__audio_enabled': True, 
                'incoming_quote': 'This Is another another the quote for celery'
            }
        ]
