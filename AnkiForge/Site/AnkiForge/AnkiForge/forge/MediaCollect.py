from google.cloud import translate_v2 as translate
import os
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "AnkiForge/Site/AnkiForge/AnkiForge/GoogleKey.json"


class Controller():

    def __init__(self, quotes):
        print(quotes)
        self.T = Translate(quotes)

class Translate():

    def __init__(self):
        self.translate_client = translate.Client()
    
