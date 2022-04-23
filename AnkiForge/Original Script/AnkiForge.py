import genanki
import imaplib, email
import re
from google.cloud import translate_v2 as translate
import nltk
from google_images_download import google_images_download   #importing the library USE WORKING JOECLINTON1 Version
import os
import shutil
import sqlite3
import datetime
import requests
import shutil
from io import BytesIO
import string


# NOTE


# Original quick, hacky script from initial development. Used only for personal computer and not used in final webapp.

# Google API Credntials JSON
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/Users/jordanwaters/Desktop/Python/Anki/KindleToAnki/KindleToAnki/My First Project-631ac9d558c9.json"
# Azure API Key
azure_key = 
azure_sub_key = 
azure_speech_key = 


to_put_media = "/Users/jordanwaters/Library/Application Support/Anki2/User 1/collection.media"
whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')

class Controller : 
    def __init__(self) : 
        self.E = Email()
        self.I = Images()
        self.C = Cards()
        # self.Gv = GVoice()
        self.Av = AVoice()
        self.D = Datastore()
        self.quotes = self.combine_lists()
        print(self.quotes)
        self.make_deck(self.quotes)
        genanki.Package(self.C.my_deck).write_to_file(f'/Users/jordanwaters/Desktop/Python/Anki/Decks/{self.get_name()}.apkg')
        # self.C.my_package.write_to_file(f'/Users/jordanwaters/Desktop/Python/Anki/Decks/{self.get_name()}.apkg')
        self.D.delete_table()
        self.E.delete_emails()

    def get_name(self) : 
        time = datetime.datetime.now()
        self.dt = time.strftime("%d.%m.%Y..%H.%M")
        return self.dt

    def combine_lists(self) : 
        self.email_quotes = self.E.get_email_quotes()
        self.browsed_words = self.D.view_all()
        return self.email_quotes + self.browsed_words

    def make_deck (self, quotes) : 
        for notes in quotes : 
            images = self.I.get_image(notes[1])
            if images :
                voices = self.Av.get_voice(notes)
                self.C.my_deck.media_files.append(images[0])
                self.C.my_deck.media_files.append(voices[0])
                my_note = genanki.Note(
                model=self.C.my_model,
                fields=[f'{notes[1]}', f'{notes[0]}', f'<img src="{images[1]}">', f'[sound:{voices[1]}]'])
                self.C.my_deck.add_note(my_note)
                shutil.copy(images[0], '/Users/jordanwaters/Library/Application Support/Anki2/User 1/collection.media')
                shutil.copy(voices[0], '/Users/jordanwaters/Library/Application Support/Anki2/User 1/collection.media')
            else:
                None
class Email : 

    def __init__ (self) : 
        self.translate_client = translate.Client()
        self.user = 'jordan.waters.kindle1@gmail.com'
        self.password = 
        self.imap_url = 'imap.gmail.com'
        self.con = imaplib.IMAP4_SSL(self.imap_url)
        self.con.login(self.user, self.password)
        self.con.SELECT('"INBOX"')


    def get_body(self, msg) : 
        if msg.is_multipart() : 
            return self.get_body(msg.get_payload(0))
        else : 
            return msg.get_payload(None, True)

    def search(self, key,value, con) : 
        result, data = self.con.search(None, key, '"{}"'.format(value))
        return data

    def get_emails(self, result_bytes) : 
        msgs = []
        for num in result_bytes[0].split():
            typ, data = self.con.fetch(num, "(RFC822)")
            msgs.append(data)
        return msgs

    def get_email_quotes(self) :
        msgs = self.get_emails(self.search('SUBJECT', 'Check out this quote', self.con))

        quotes = []
        for msg in msgs :
            example = self.get_body(email.message_from_bytes(msg[0][1]))
            text = re.findall(r'"([^"]*)"', example.decode("utf-8"))
            # Quick get around, problems with punctuation being transalted weirldy and there for not finding any
            # image search results
            clean_text = "".join([x for x in text[0] if x not in [",","«","»",":"]])
            quotes.append(clean_text)
        if quotes : 
            translations = self.translate_words(quotes)
            return translations
        else :
            return []

    def translate_words(self, quotes) : 
        results = self.translate_client.translate(
            quotes, source_language = 'es', target_language = 'en'
        )
        print()
        return [[x['input'], x['translatedText']] for x in results]

    def delete_emails (self) : 
        typ, data = self.con.search(None, 'ALL')
        for num in data[0].split():
            self.con.store(num, '+FLAGS', '\\Deleted')
        self.con.expunge()
        self.con.close()
        self.con.logout()


class Images : 
    def __init__(self):
        self.response = google_images_download.googleimagesdownload()
        self.subscription_key = azure_images_sub_key
        self.search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
        self.headers = {"Ocp-Apim-Subscription-Key" : self.subscription_key}

    def get_nouns(self, phrase):
        sentence = nltk.sent_tokenize(phrase) #tokenize sentences
        nouns = [] #empty to array to hold all nouns
        for word,pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
                if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS'):
                    nouns.append(word)
        words = " ".join(nouns)
        searchable = ''.join(filter(whitelist.__contains__, words))
        return searchable


    # def search(self, sub_or_phrase) : 
    #     arguments = {"keywords":f"{sub_or_phrase}",
    #             "limit":1,
    #             "print_urls":False,
    #             "size" : ">1024*768",
    #             "output_directory" : "/Users/jordanwaters/Desktop/TerminalScripts/Kindleimg",
    #             "no_directory" : "/Users/jordanwaters/Desktop/TerminalScripts/Kindleimg",
    #             }   #creating list of arguments
    #     paths = self.response.download(arguments)   #passing the arguments to the function
    #     file_name = sub_or_phrase.replace(" ", "")
    #     path = paths[0]
    #     search, file = list(path.items())[0]
    #     file_path = "".join(file)
    #     file_type = file_path[-4:]
    #     file_name = file_name + file_type

    #     os.rename(file_path, f"/Users/jordanwaters/Desktop/TerminalScripts/Kindleimg/{file_name}")
    #     return (f"/Users/jordanwaters/Desktop/TerminalScripts/Kindleimg/{file_name}", file_name)

    def search(self, sub_or_phrase):
        """  Added if to remove if no results for search """
        params  = {"q": sub_or_phrase, "license": "public"}
        response = requests.get(self.search_url, headers = self.headers, params=params)
        response.raise_for_status()
        search_results = response.json()
        print(search_results)
        if search_results['value']:
            thumbnail_url = [img["thumbnailUrl"] for img in search_results["value"][:1]][0]
            encoding_format = [img["encodingFormat"] for img in search_results["value"][:1]][0]

            filename = f"{sub_or_phrase.replace(' ', '')}.{encoding_format}"
            filepath = f"/Users/jordanwaters/Desktop/TerminalScripts/Kindleimg/{filename}"
            r = requests.get(thumbnail_url, stream = True)
            if r.status_code == 200:
                r.raw.decode_content = True                
                with open(filepath,'wb') as f:
                    shutil.copyfileobj(r.raw, f)                    
                print('Image sucessfully Downloaded: ',filename)
                return (filepath, filename)
            else:
                print('Image Couldn\'t be retreived')
        else:
            return False


    def get_image(self, phrase):
        phrase = "".join([x for x in phrase if x in whitelist]) 
        sub = (self.get_nouns(phrase))
        if sub.replace(" ", "") : 
            return self.search(sub)
        else : 
            return self.search(phrase)

class Cards :
    def __init__(self):
        """ Normal deck"""
        # self.my_deck = genanki.Deck(
        #     1041609453,
        #     'Spanish')
        """New Deck"""
        # self.my_deck = genanki.Deck(
        #     1041609443,
        #     'Spanish Cram')
        self.my_deck = genanki.Deck(
            1041609457,
            'Test')
        self.my_deck.media_files = []
        """Normal Model"""
        # self.my_model = genanki.Model(
        #     1041609445,
        #     'Basic (and reversed card)',
        #     css="""
        #         .card {
        #         font-family: arial;
        #         font-size: 20px;
        #         text-align: center;
        #         color: black;
        #         background-color: white;
        #         }
        #         .media {
        #         margin: 2px;
        #         }
        #     """,
        #     fields=[
        #         {'name': 'Question'},
        #         {'name': 'Answer'},
        #         {'name': 'MyMedia'},
        #         {'name': 'MyAudio'}, 
        #     ],
        #     templates=[
        #         {
        #             'name': 'Card 1',
        #             'qfmt': '{{Question}}<br>{{MyMedia}}',
        #             'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{MyAudio}}',
        #         }, 
        #         {
        #             'name': 'Card 2',
        #             'qfmt': '{{Answer}}<br>{{MyAudio}}',
        #             'afmt': '{{FrontSide}}<hr id="answer">{{Question}}<br>{{MyMedia}}',
        #         },         
        #     ])
        """New Model"""
        self.my_model = genanki.Model(
            1041609445,
            'Basic (and reversed card)',
            css="""
                .card {
                font-family: arial;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
                }
                .media {
                margin: 2px;
                }
            """,
            fields=[
                {'name': 'Question'},
                {'name': 'Answer'},
                {'name': 'MyMedia'},
                {'name': 'MyAudio'}, 
            ],
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '{{Question}}<br>{{MyMedia}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{MyAudio}}',
                }, 
                {
                    'name': 'Card 3',
                    'qfmt': '{{MyAudio}}',
                    'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}<br>{{Question}}<br>{{MyMedia}}',
                },           
            ])

class Datastore : 

    def __init__(self): 
        self.conn = sqlite3.connect('/Users/jordanwaters/Desktop/TerminalScripts/BrowserWords1')
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS newwords (english TEXT, spanish TEXT)")
        self.cur.execute("CREATE TABLE IF NOT EXISTS backup (english TEXT, spanish TEXT)")
        self.conn.commit()
    
    def add_entry(self, english, spanish) : 
        self.cur.execute("INSERT INTO newwords VALUES (?, ?)", (english, spanish))
        self.conn.commit()
    
    def view_all(self):
        self.cur.execute('''SELECT count(name) FROM sqlite_master WHERE type ='table' AND name ='newwords' ''')
        if self.cur.fetchone()[0] : 
            self.cur.execute("SELECT * FROM newwords")
            rows = self.cur.fetchall()
            return rows
        else :
            return []

    def view_all_backup(self) : 
        self.cur.execute("SELECT * FROM backup")
        rows = self.cur.fetchall()
        return rows

    def delete_table(self) : 
        self.cur.execute("INSERT INTO backup SELECT * FROM newwords")
        self.cur.execute("DROP TABLE newwords")
        self.conn.commit()

    def __del__ (self) : 
        self.conn.close()

class GVoice : 

    def __init__(self): 
        from google.cloud import texttospeech
        self.texttospeech = texttospeech
        self.client = self.texttospeech.TextToSpeechClient()

    def get_voice(self, quote) :
        # Send through both, use english for filename
        synthesis_input=self.texttospeech.SynthesisInput(text=f"{quote[0]}")
        voice = self.texttospeech.VoiceSelectionParams(
            language_code='es-ES',
            name='es-ES-Standard-A',
            ssml_gender=2
            )
        audio_config = self.texttospeech.AudioConfig(
            audio_encoding = self.texttospeech.AudioEncoding.MP3
            )
        response = self.client.synthesize_speech(
            input = synthesis_input, voice = voice, audio_config= audio_config
            )
        clean_name = "".join([x for x in quote[1] if x in whitelist])
        filename = clean_name.replace(" ", "") + ".mp3"    
        full_filename = f"/Users/jordanwaters/Desktop/TerminalScripts/Kindleaudio/{filename}"
        with open(full_filename, 'wb') as out : 
            out.write(response.audio_content)
        return [full_filename, filename]

class AVoice : 
    def __init__(self) : 
        import azure.cognitiveservices.speech as speechsdk
        self.speechsdk = speechsdk
        self.speech_key, self.service_region = azure_speech_key, "uksouth"
    
    def get_voice(self, quote) : 
        print(quote)
        speech_config = self.speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
        voice = "Microsoft Server Speech Text to Speech Voice (es-ES, ElviraNeural)"
        speech_config.speech_synthesis_voice_name = voice
        speech_config.set_speech_synthesis_output_format(self.speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3)
        clean_name = "".join([x for x in quote[1] if x in whitelist])
        file_name = clean_name.replace(" ", "") + ".mp3"   
        full_filename = f"/Users/jordanwaters/Desktop/TerminalScripts/Kindleaudio/{file_name}"
        file_config = self.speechsdk.audio.AudioOutputConfig(filename=full_filename)
        speech_synthesizer = self.speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=file_config)
        result = speech_synthesizer.speak_text_async(quote[0]).get()
        return [full_filename, file_name]



Controller()
