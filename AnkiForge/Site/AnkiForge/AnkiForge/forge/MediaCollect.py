from google.cloud import translate_v2 as translate
import os
import six
"""THIS MODULE SHOULD RECIVE SINGLE DICTIONARYS"""
""" WHEN RUNNING THROUGH DOCKER UNCOMMENT THIS """

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/code/GoogleKey.json"

"""WHEN RUNNING TESTING UNCOMMENT THIS"""

# The taask will pass the data like this as a query set, which can be treated as a dictionary
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/jordanwaters/Desktop/Python/GitHubRepositories/AnkiForge/AnkiForge/Site/AnkiForge/AnkiForge/GoogleKey.json"


# To begin, take input text, detect lang, translate to target lang
class Controller():

    def __init__(self, quote):
        # At this point we are handed quote with a 
        self.quote = quote

        # Here we translate the quote
        self.T = Translate(self.quote)
        self.translated_result = self.T.translation_result
        # print(self.translated_result)

        # here is the resultant dictionary we will return
        self.result = self.quote



class Translate():

    def __init__(self, quote):
        self.translate_client = translate.Client()
        # but first we need the language

        self.detection_result = self.detect_language(quote)
        
        # translate
        self.translation_result = self.make_translation(quote, 'es')
        
    def detect_language(self, quote):
        detecting_string = quote['incoming_quote'][0:10]
        quote['original_language']= self.translate_client.detect_language(detecting_string)
        print(quote['original_language'])

    def make_translation(self, quote, target):
        result = self.translate_client.translate(quote['incoming_quote'], target_language=target)
        quote['translated_quote'] = result['translatedText']
        quote['translated_language']= target        
        return quote
        # ready_quotes = [quote['incoming_quote'] for quote in quote]
        # results = self.translate_client.translate(ready_quotes, target_language=target)
        # for quote, result in zip(quote, results):
        #     quote['translated_quote'] = result['translatedText']
        #     quote['translated_language']= target
        # return quote 


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
mixed_quotes = [
            {
                'id': 2, 'user_id': 1, 'deck_id': 1,
                'deck__learnt_lang': 'es', 'deck__native_lang': 'en',
                'deck__images_enabled': True, 'deck__audio_enabled': True,
                'incoming_quote': 'You would deeply regret it if you lost it all'
            },
            {
                'id': 1, 'user_id': 1, 'deck_id': 1, 
                'deck__learnt_lang': 'en', 'deck__native_lang': 'es', 
                'deck__images_enabled': True, 'deck__audio_enabled': True, 
                'incoming_quote': 'Me parece que esto es un otro cita'
            },
            {
                'id': 1, 'user_id': 1, 'deck_id': 1, 
                'deck__learnt_lang': 'fr', 'deck__native_lang': 'en', 
                'deck__images_enabled': True, 'deck__audio_enabled': True, 
                'incoming_quote': 'This Is another the quote for celery'
            },
            {
                'id': 1, 'user_id': 1, 'deck_id': 1, 
                'deck__learnt_lang': 'es', 'deck__native_lang': 'fr', 
                'deck__images_enabled': True, 'deck__audio_enabled': True, 
                'incoming_quote': 'Je pouvais entendre mes colocataires'
            }
        ]

def test_and_time_easy():
    import time
    finished_quote = []
    for quote in quotes:
        time_1 = time.perf_counter()
        test_1 = Controller(quote)
        time_2 = time.perf_counter()
        elapsed_1 = time_2-time_1

        print(f"***TIME ELAPSED FOR SENDING FOUR ITEMS IN UN GOLPE == {elapsed_1}***")
        finished_quote.append(test_1.translated_result)
    time.sleep(10)

    print(finished_quote)

def test_and_time_hard():
    import time
    finished_quote = []
    for quote in mixed_quotes:
        time_1 = time.perf_counter()
        test_1 = Controller(quote)
        time_2 = time.perf_counter()
        elapsed_1 = time_2-time_1

        print(f"***TIME ELAPSED FOR SENDING FOUR ITEMS IN UN GOLPE == {elapsed_1}***")
        finished_quote.append(test_1.translated_result)
    time.sleep(10)

    print(finished_quote)

def test_and_time_single_easy():
    import time

    quote = quotes[0]
    time_1 = time.perf_counter()
    test_1 = Controller(quote)
    time_2 = time.perf_counter()
    elapsed_1 = time_2-time_1
    print(test_1.translated_result)
    print(f"***TIME ELAPSED FOR SENDING FOUR ITEMS IN UN GOLPE == {elapsed_1}***")

# test_and_time_single_easy()
# test_and_time_hard()