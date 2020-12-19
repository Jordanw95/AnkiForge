from google.cloud import translate
import os
import six
import time
"""THIS MODULE SHOULD RECIVE SINGLE DICTIONARYS"""
""" WHEN RUNNING THROUGH DOCKER UNCOMMENT THIS """

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/code/SecretKeys/ankiforge-05bc6fd7128b.json"

"""WHEN RUNNING TESTING UNCOMMENT THIS"""

# The taask will pass the data like this as a query set, which can be treated as a dictionary
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/jordanwaters/Desktop/Python/GitHubRepositories/AnkiForge/AnkiForge/Site/AnkiForge/AnkiForge/SecretKeys/ankiforge-05bc6fd7128b.json"


# To begin, take input text, detect lang, translate to target lang
class Controller():

    def __init__(self, quote):
        # At this point we are handed quote with a 
        self.quote = quote

        # Here we translate the quote
        self.T = Translate(self.quote)
        self.translated_result = self.T.translation_result
        # here is the resultant dictionary we will return




class Translate():

    def __init__(self, quote):
        # Initialise and set variables
        self.translate_client = translate.TranslationServiceClient()
        self.location = "global"
        self.project_id = "ankiforge"
        self.parent = f"projects/{self.project_id}/locations/{self.location}"
        # Make a suitable sized string for detection
        self.detection_quote = self.get_detect_sample(quote)
        #  we need the language
        self.detection_result = self.detect_language(self.detection_quote)
        # translate
        self.translation_result = self.make_translation(self.detection_result)
        
    def get_detect_sample(self, quote):
        #Is a way to try and send less complete words to detect and save some money
        split_string = quote['incoming_quote'].split()
        reduced_quote = split_string[:5]
        quote['detection_quote'] = " ".join(reduced_quote)
        return quote

    def detect_language(self, quote):
        response = self.translate_client.detect_language(
            content=quote['detection_quote'],
            parent=self.parent,
            mime_type="text/plain",  # mime types: text/plain, text/html
        )
        for language in response.languages:
            quote['original_language']=language.language_code
            # First two due to issues with different chinese languages
            if quote['original_language'][:2] == quote['deck__learnt_lang'][:2]:
                quote['translated_language']= quote['deck__native_lang']
            else:
                quote['translated_language']= quote['deck__learnt_lang']
        return quote

        # quote['original_language']= self.translate_client.detect_language(detecting_string)
        # print(quote['original_language'])

    def make_translation(self, quote):
        response = self.translate_client.translate_text(
            request={
                "parent": self.parent,
                "contents": [quote['incoming_quote']], #whatever you put here will be itereated over
                "mime_type": "text/plain",  # mime types: text/plain, text/html
                "source_language_code": quote['original_language'],
                "target_language_code": quote['translated_language'],
            }
        )
        for translation in response.translations:
            quote['translated_quote']=translation.translated_text
        return quote



"""WHEN RUNNING TESTING UNCOMMENT THIS"""

# quotes = [
#             {
#                 'id': 2, 'user_id': 1, 'deck_id': 1,
#                 'deck__learnt_lang': 'es', 'deck__native_lang': 'en',
#                 'deck__images_enabled': True, 'deck__audio_enabled': True,
#                 'incoming_quote': 'You would'
#             },
#             {
#                 'id': 1, 'user_id': 1, 'deck_id': 1, 
#                 'deck__learnt_lang': 'es', 'deck__native_lang': 'en', 
#                 'deck__images_enabled': True, 'deck__audio_enabled': True, 
#                 'incoming_quote': 'This Is the quote for celery'
#             },
#             {
#                 'id': 1, 'user_id': 1, 'deck_id': 1, 
#                 'deck__learnt_lang': 'es', 'deck__native_lang': 'en', 
#                 'deck__images_enabled': True, 'deck__audio_enabled': True, 
#                 'incoming_quote': 'This Is another the quote for celery'
#             },
#             {
#                 'id': 1, 'user_id': 1, 'deck_id': 1, 
#                 'deck__learnt_lang': 'es', 'deck__native_lang': 'en', 
#                 'deck__images_enabled': True, 'deck__audio_enabled': True, 
#                 'incoming_quote': 'This Is another another the quote for celery'
#             },
#         ]
# mixed_quotes = [
#             {
#                 'id': 2, 'user_id': 1, 'deck_id': 1,
#                 'deck__learnt_lang': 'es', 'deck__native_lang': 'en',
#                 'deck__images_enabled': True, 'deck__audio_enabled': True,
#                 'incoming_quote': 'You would deeply regret it if you lost it all'
#             },
#             {
#                 'id': 1, 'user_id': 1, 'deck_id': 1, 
#                 'deck__learnt_lang': 'en', 'deck__native_lang': 'es', 
#                 'deck__images_enabled': True, 'deck__audio_enabled': True, 
#                 'incoming_quote': 'Me parece que esto es un otro cita'
#             },
#             {
#                 'id': 1, 'user_id': 1, 'deck_id': 1, 
#                 'deck__learnt_lang': 'fr', 'deck__native_lang': 'en', 
#                 'deck__images_enabled': True, 'deck__audio_enabled': True, 
#                 'incoming_quote': 'This Is another the quote for celery'
#             },
#             {
#                 'id': 1, 'user_id': 1, 'deck_id': 1, 
#                 'deck__learnt_lang': 'es', 'deck__native_lang': 'fr', 
#                 'deck__images_enabled': True, 'deck__audio_enabled': True, 
#                 'incoming_quote': 'Je pouvais entendre mes colocataires'
#             },
#             {
#                 'id': 1, 'user_id': 1, 'deck_id': 1, 
#                 'deck__learnt_lang': 'es', 'deck__native_lang': 'fr', 
#                 'deck__images_enabled': True, 'deck__audio_enabled': True, 
#                 'incoming_quote': 'おはようございます'
#             }
#         ]

# def test_and_time_easy():
#     import time
#     finished_quote = []
#     for quote in quotes:
#         time_1 = time.perf_counter()
#         test_1 = Controller(quote)
#         time_2 = time.perf_counter()
#         elapsed_1 = time_2-time_1

#         print(f"***TIME ELAPSED FOR SENDING FOUR ITEMS IN UN GOLPE == {elapsed_1}***")
#         finished_quote.append(test_1.translated_result)
#     time.sleep(10)

#     print(finished_quote)

# def test_and_time_hard():
#     import time
#     finished_quote = []
#     for quote in mixed_quotes:
#         time_1 = time.perf_counter()
#         test_1 = Controller(quote)
#         time_2 = time.perf_counter()
#         elapsed_1 = time_2-time_1

#         print(f"***TIME ELAPSED FOR SENDING FOUR ITEMS IN UN GOLPE == {elapsed_1}***")
#         finished_quote.append(test_1.translated_result)
#     time.sleep(10)

#     print(finished_quote)

# def test_and_time_single_easy():
#     import time

#     quote = quotes[0]
#     time_1 = time.perf_counter()
#     test_1 = Controller(quote)
#     time_2 = time.perf_counter()
#     elapsed_1 = time_2-time_1
#     print(test_1.translated_result)
#     print(f"***TIME ELAPSED FOR SENDING ONE ITEM IN UN GOLPE == {elapsed_1}***")

# # test_and_time_single_easy()
# # test_and_time_hard()
# test_and_time_hard()