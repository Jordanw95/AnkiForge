from google.cloud import translate
import os
import six
import time
from azure.cognitiveservices.speech import AudioDataStream, SpeechConfig, SpeechSynthesizer, SpeechSynthesisOutputFormat
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from xml.etree import ElementTree
import string
import boto3
from botocore.exceptions import NoCredentialsError
from nltk import word_tokenize, pos_tag
import requests
import io
import shutil
from decks.models import ArchivedCards

"""THIS MODULE SHOULD RECIVE SINGLE DICTIONARYS"""
""" WHEN RUNNING THROUGH DOCKER UNCOMMENT THIS """

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/code/SecretKeys/ankiforge-05bc6fd7128b.json"

"""WHEN RUNNING TESTING UNCOMMENT THIS"""

# To begin, take input text, detect lang, translate to target lang
class Controller():

    def __init__(self, quote):
        # At this point we are handed quote with a 
        self.quote = quote
        self.quote['incoming_quote'] = quote['incoming_quote'].lower()
        # Here we translate the quote
        self.T = Translate(self.quote)
        self.translated_result = self.T.translation_result
        # Need to filter to correct processes
        # Instead of long else if here - could have if else and then determine whether to run image and audio individually within AzureVoiceController and AzureImageController
        if self.translated_result['deck__audio_enabled'] == False and self.translated_result['deck__images_enabled'] == False:
            self.final_result = self.translated_result
            self.final_result['upload_audio_success']=False
            self.final_result['upload_image_success']=False
            self.final_result['audio_found_in_db']= False
            self.final_result['image_found_in_db'] = False
        else:
            # Send to both and determine within each. 
            # Will need to return success results for each too
            self.translated_result = self.set_config(self.translated_result)
            # regardless of outcome of search I need to set media found
            self.translated_and_searched_result = self.search_db(self.translated_result)

            self.voicecontroller = VoiceController(self.translated_and_searched_result)
            self.voice_processed = self.voicecontroller.voice_processed_quote
            # Then send to image
            print("**** QUOTE BEFORE SENT TO IMAGE CONTROLLER***")
            self.imagecontroller = ImageController(self.voice_processed)
            self.image_processed = self.imagecontroller.final_image_processed_quote
            # after
            self.final_result = self.image_processed
            print(self.final_result)

    def set_config(self, quote):
        # Need to collect        
        quote['xml_lang'] = language_codes[(quote['deck__learnt_lang'])]
        quote['voice_name'] = voice_codes[(quote['deck__learnt_lang'])]
        # Send quote in the learnt lang, first two charecters used becuase of chinese inaccuracy in detect
        if quote['deck__learnt_lang'][:2]==quote['original_language'][:2]:
            quote['voiced_quote'] = quote['incoming_quote']
            quote['voiced_quote_lang'] = quote['original_language']
        elif quote['deck__learnt_lang'][:2]==quote['translated_language'][:2]:
            quote['voiced_quote']=quote['translated_quote']
            quote['voiced_quote_lang'] = quote['translated_language']
        else:
            print('***********************************************')
            print('******ERROR IN SET_CONFIG FOR VOICE AND SEARCH *******')
            print('***********************************************')
        return quote

    def search_db(self, quote):
        if quote['deck__audio_enabled'] == True and quote['deck__images_enabled'] == True:
            # Search DB using voiced quote with query set that incluides all enabled
            self.search_results =ArchivedCards.duplicate_archive_search_objects.filter(voiced_quote=quote['voiced_quote'], voiced_quote_lang = quote['voiced_quote_lang'])
            # This will return a quesry set, if it is full, need to set all parameters based on it and then passing it through all the other steps should do this without problems
            # The better option would be to just be able to pass back the archived object ID and save the incoming card with a realtionship to it, would save making a new archivedobject
            # This will required editing the tasks.py and removing all the found_in_db parametersa and if. probs best though.
            if self.search_results:
                self.archived_card = self.search_results.first()
                quote['image_found_in_db'] = True
                quote['audio_found_in_db'] = True
                quote['archived_card_id'] = self.archived_card.id
                return quote
            else: 
                quote['audio_found_in_db'] = False
                quote['image_found_in_db'] = False
                return quote
            
        else: 
            quote['audio_found_in_db'] = False
            quote['image_found_in_db'] = False
            return quote

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
        # the majority of the time it should match one of these and there is no problem
        # however sometimes detect is poor *asian language* so need to resort to else where we assume poorly translated is 
        # the learnt language and not english
        if quote['original_language'][:2] == quote['deck__learnt_lang'][:2] or quote['original_language'][:2] == quote['deck__native_lang'][:2]:
            pass
        else : 
            quote['translated_language']= quote['deck__native_lang']
            quote['original_language'] = quote['deck__learnt_lang']
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

voice_codes = {
    'es' : 'es-ES-AlvaroNeural',
    'ja' : 'ja-JP-KeitaNeural',
    'zh-CN' : 'zh-CN-YunyangNeural',
    'zh-TW' : 'zh-TW-YunJheNeural',
    'de' : 'de-DE-ConradNeural',
    'it' : 'it-IT-DiegoNeural',
    'fr' : 'fr-FR-HenriNeural',
}

language_codes = {
    'es' : 'es-ES',
    'ja' : 'ja-JP',
    'zh-CN' : 'zh-CN',
    'zh-TW' : 'zh-TW',
    'de' : 'de-DE',
    'it' : 'it-IT',
    'fr' : 'fr-FR',
}

class VoiceController():
    
    def __init__(self, quote):
        # include in self.quote the config for voice
        self.quote = quote
        if self.quote['deck__audio_enabled']:
            if self.quote['audio_found_in_db']:
                print("***AUDIO FOUND IN DB***")
                self.voice_processed_quote = self.quote
            else:
                self.AzureVoiceIn = AzureVoice(self.quote)
                # Azure voice quote 
                self.voice_processed_quote = self.AzureVoiceIn.finished_voiced_quote
                # upload to s3
                self.UploadS3AudioIn = UploadS3Audio(self.voice_processed_quote)
                # final returned dict 
                self.voice_processed_quote= self.UploadS3AudioIn.finished_uploaded_quote
        else:
            # May need to approach difference between failed upload and not wanted upload
            self.quote['upload_audio_success']= False
            self.voice_processed_quote = self.quote



class AzureVoice():
    
    def __init__(self, quote):
        # build audio config
        # self.quote_with_codes = self.set_config(quote)
        self.quote_with_xml_file = self.create_xml(quote)
        self.finished_voiced_quote = self.request_voice(self.quote_with_xml_file)
    

    def create_xml(self, quote):
        #here will need to write an XML file using element tree to send parameters to the api
        # https://stackabuse.com/reading-and-writing-xml-files-in-python/
        speak = ElementTree.Element('speak', {
            'version' : "1.0",
            'xmlns' : "http://www.w3.org/2001/10/synthesis",
            'xml:lang' : quote['xml_lang'],
        })
        voice = ElementTree.SubElement(speak, 'voice', {'name':quote['voice_name']})
        voice.text = quote['voiced_quote']
        # write to xml file to be used for each api request
        # Might need to change encoding for chinese and japanese, try after
        # https://stackoverflow.com/questions/10046755/write-xml-utf-8-file-with-utf-8-data-with-elementtree
        quote['xml_filename'] = "forge/recycled_xml_for_api.xml"
        voice_data = ElementTree.tostring(speak)
        voice_file=open(quote['xml_filename'], "wb+")
        voice_file.write(voice_data)
        return quote
    
    def request_voice(self, quote):
        self.speech_config = SpeechConfig(subscription=os.environ['AZURE_KEY'], region=os.environ['AZURE_REGION'])
        # it works to save_to_wave file as .mp3 and this file can be loaded in anki
        self.speech_config.set_speech_synthesis_output_format(SpeechSynthesisOutputFormat['Audio16Khz64KBitRateMonoMp3'])
        self.synthesizer = SpeechSynthesizer(speech_config=self.speech_config, audio_config=None)
        # Need to address filenaming
        self.ssml_string = open(quote['xml_filename'], "r").read()
        self.result = self.synthesizer.speak_ssml_async(self.ssml_string).get()

        self.stream = AudioDataStream(self.result)
        quote = self.create_universal_filename(quote)
        # No need to partition files locally
        quote['local_file_path']= f"forge/audio/{quote['universal_audio_filename']}"
        self.stream.save_to_wav_file(quote['local_file_path'])
        return quote

    def create_universal_filename(self, quote):
        # This needs to be looked at for scale use this link
        # https://stackoverflow.com/questions/47529120/save-sentence-as-server-filename
        # https://stackoverflow.com/questions/3006710/python-unhash-value
        # self.simplified_quote = quote['voiced_quote'].translate({ord(c): None for c in string.whitespace})
        # hashing should be fine aslong as I dont lose ArchivedDB
        self.hashed_quote = hash(quote['voiced_quote'])
        quote['universal_audio_filename'] = f"{self.hashed_quote}.mp3"
        return quote

class UploadS3Audio():
    
    def __init__(self, quote):
        self.s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
        # upload to s3
        self.finished_uploaded_quote = self.upload_to_s3(quote)
        # return location 
    
    def upload_to_s3(self, quote):
        # Create s3 file path
        quote['aws_audio_file_path']= f"audio/{quote['voiced_quote_lang']}/{quote['universal_audio_filename']}"
        # Save to file path, may need to allow for more errors
        try:
            self.s3.upload_file(quote['local_file_path'], os.environ['AWS_STORAGE_BUCKET_NAME'], quote['aws_audio_file_path'])
            quote['upload_audio_success'] = True
        except FileNotFoundError:
            print("The file was not found")
            quote['upload_audio_success'] = False
        except NoCredentialsError:
            print("Credentials not available")
            quote['upload_audio_success'] = False    
        # return with dictionary file path
        return quote


class ImageController():
    """ This will take quote directly from controller, determine if image is required, Should be told before hand if result is already in DB and if it is not found it will send a request to AzureBingSearch"""
    def __init__(self, quote):
        # Check we should be looking for images
        if quote['deck__images_enabled']:
            if quote['image_found_in_db']:
                self.final_image_processed_quote = quote
            else:
                self.image_processed_quote = self.collect_image(quote)
                self.final_image_processed_quote = self.upload_new_image_s3(self.image_processed_quote)
        else:
            self.final_image_processed_quote = self.no_image_required(quote)
        # Check if image is already in DB

    def collect_image(self, quote):
        self.smartfilter = SmartFilter(quote)
        self.filtered_for_search_quote=self.smartfilter.with_searchable_quote
        self.azure_image = AzureImage(self.filtered_for_search_quote)
        self.quote = self.azure_image.quote_with_local_filepath
        self.quote['image_found_in_db'] = False
        return self.quote

    def no_image_required(self, quote):
        quote['upload_image_success']=False
        quote['image_found_in_db'] = False
        return quote

    def upload_new_image_s3(self, quote):
        self.uploadimages3 = UploadS3Image(quote)
        quote = self.uploadimages3.finished_upload_image
        return quote

class AzureImage():
    
    def __init__(self, quote):
        self.azure_key = os.environ['AZURE_SEARCH_KEY']
        self.quote_with_collected_image = self.make_request(quote)
        print(self.quote_with_collected_image)
        self.quote_with_local_filepath = self.download_image(self.quote_with_collected_image, 0)
        print(self.quote_with_local_filepath)

    def make_request(self, quote):
        self.search_term = quote['image_search_phrase_string']
        self.params = {
            "q": self.search_term,
            "license": "public", 
            "imageType":"photo",
            "size":"Large",
            "maxWidth":"800",
            "maxHeight":"800",
            "aspect": "Square"
            }
        self.headers = {"Ocp-Apim-Subscription-Key" : self.azure_key}
        self.search_url = "https://api.bing.microsoft.com/v7.0/images/search"
        self.response = requests.get(self.search_url, headers = self.headers, params = self.params)
        self.response.raise_for_status()
        self.search_results=self.response.json()
        # Retrieve the value that contains all image results and info
        self.value = self.search_results['value']
        # Save the first image results url path
        self.urls_list = []
        for object in self.value:
            image_url = object['contentUrl']
            image_filetype = object['encodingFormat']
            self.urls_list.append({'image_url':image_url, 'image_filetype': image_filetype})
        quote['image_urls_list'] = self.urls_list
        return quote

    def download_image(self, quote, attempt):
        self.links_available = len(quote['image_urls_list'])
        if attempt > self.links_available:
            raise Exception("ALL AVAILABLE IMAGE DOWNLOAD LINKS HAVE BEEN ATTEMPTED")
        else: 
            quote = self.create_universal_image_filename(quote, attempt)
            self.filepath = f"forge/images/{quote['universal_image_filename']}"
            self.r = requests.get(quote['image_urls_list'][attempt]['image_url'], stream=True)
            # Error appears to be that this specific download link doesn't work, add logic to try multiple
            print(self.r)
            if self.r.status_code == 200:
                print(f'*IMAGE DOWNLOAD ATTEMPT SUCCEEDED ON ATTEMPT {attempt} OF {self.links_available} *')
                self.r.raw.decode_content = True
                quote['retrieved_image_url'] = quote['image_urls_list'][attempt]['image_url']
                print(f'*IMAGE Beginning download to {self.filepath}*')
                del quote['image_urls_list']
                with open(self.filepath, 'wb') as f:
                    shutil.copyfileobj(self.r.raw, f)
                    print('Image downloaded')
                    quote['local_image_filepath'] = self.filepath
                    print(quote)
                    return(quote)
            else:
                print(f'*IMAGE DOWNLOAD ATTEMPT {attempt} OF {self.links_available} FAILED WITH RESPONSE {self.r}*')
                attempt += 1
                quote = self.download_image(quote, attempt)
        return quote
    
    def create_universal_image_filename(self, quote, attempt):
        self.hashed_quote = hash(quote['image_search_phrase_string'])
        # this may cuase errors, may want to look for only certain filetypes and use them, see as and when you get errors further through testing
        encoding_formats={
            'jpeg':'jpg',
            'png':'png',
            'bmp' : 'bmp',
        }
        # Need to address filetype properly at some point.
        quote['universal_image_filename'] = f"{self.hashed_quote}.{encoding_formats[quote['image_urls_list'][attempt]['image_filetype']]}"
        return quote



class SmartFilter():
    """Should any translated phrase and return an appropriate search string"""
    def __init__(self, quote):
        self.with_english_quote = self.get_english_quote(quote)
        self.test_length = len(quote['english_quote'].split())
        if self.test_length < 4:
            self.with_searchable_quote = self.small_quote(self.with_english_quote)


        else:
            self.with_searchable_quote = self.get_searchable(self.with_english_quote)
    
    def small_quote(self, quote):
        quote['image_search_phrase_list']=quote['english_quote'].split()
        quote['image_search_phrase_string']= quote['english_quote']
        return quote

    def get_english_quote(self, quote):
        if quote['original_language'] == 'en':
            quote['english_quote'] = quote['incoming_quote']
        else:
            quote['english_quote'] = quote['translated_quote']
        return quote

    def get_searchable(self, quote):
        self.token = word_tokenize(quote['english_quote'])
        self.tagged = pos_tag(self.token)
        # return struct [('word', 'NN')]
        # check returns somthing, all need to be formatted as a list
        if self.ideal_clean_attempt(self.tagged):
            quote['image_search_phrase_list'] = self.ideal_clean_attempt(self.tagged)
        # if not send back to second clean
        elif self.second_clean_attempt(self.tagged):
            quote['image_search_phrase_list'] = self.second_clean_attempt(self.tagged)
        # if still no just set whole string
        else: 
            quote['image_search_phrase_list'] = self.token
        # check result not too long
        # shorten if it is
        if len(quote['image_search_phrase_list']) > 4 :
            quote['image_search_phrase_list'] = quote['image_search_phrase_list'][:3]
        # send back
        quote['image_search_phrase_string'] = " ".join(quote['image_search_phrase_list'])
        return quote


    def ideal_clean_attempt(self, tagged):
        self.ok_tags = ['NN', 'NNP', 'NNS', 'NNPS', 'NNPS', 'VBD']
        self.result = [x[0] for x in tagged if x[1] in self.ok_tags]
        return self.result
    
    def second_clean_attempt(self, tagged):
        self.ok_tags = ['NN', 'NNP', 'NNS', 'NNPS', 'NNPS', 'VBD', 'JJ', 'VB', 'PRP']
        self.result = [x[0] for x in tagged if x[1] in self.ok_tags]
        return self.result

class UploadS3Image():
    
    def __init__(self, quote):
        self.s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
        # upload to s3
        self.finished_upload_image = self.upload_image_to_s3(quote)
        # return location 
    
    def upload_image_to_s3(self, quote):
        # just gonnan save image locally first dynamic transfer seems inconsistent
        quote['aws_image_file_path']= f"images/{quote['universal_image_filename']}"
        # Save to file path, may need to allow for more errors
        print('*IMAGE begginging upload to s3*')
        try:
            self.s3.upload_file(quote['local_image_filepath'], os.environ['AWS_STORAGE_BUCKET_NAME'], quote['aws_image_file_path'])
            quote['upload_image_success'] = True
            print('*IMAGE UPLOADED*')
        except FileNotFoundError:
            print("The file was not found")
            quote['upload_audio_success'] = False
        except NoCredentialsError:
            print("Credentials not available")
            quote['upload_audio_success'] = False    
        # return with dictionary file path
        return quote