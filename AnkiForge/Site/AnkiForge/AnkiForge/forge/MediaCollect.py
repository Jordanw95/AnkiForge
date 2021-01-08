from google.cloud import translate
import os
import six
import time
"""THIS MODULE SHOULD RECIVE SINGLE DICTIONARYS"""
""" WHEN RUNNING THROUGH DOCKER UNCOMMENT THIS """

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/code/SecretKeys/ankiforge-05bc6fd7128b.json"

"""WHEN RUNNING TESTING UNCOMMENT THIS"""

# To begin, take input text, detect lang, translate to target lang
class Controller():

    def __init__(self, quote):
        # At this point we are handed quote with a 
        self.quote = quote
        # Here we translate the quote
        self.T = Translate(self.quote)
        self.translated_result = self.T.translation_result
        # Need to filter to correct processes
        # Instead of long else if here - could have if else and then determine whether to run image and audio individually within AzureVoiceController and AzureImageController
        if self.translated_result['deck__audio_enabled'] == False and self.translated_result['deck__images_enabled'] == False:
            self.final_result = self.translated_result
            self.final_result['upload_audio_success']=False
            self.final_result['upload_image_success']=False
        else:
            # Send to both and determine within each. 
            # Will need to return success results for each too
            self.AzureVoice = AzureVoiceController(self.translated_result)
            self.azure_voice_processed = self.AzureVoice.azure_voice_processed_quote
            # Then send to image

            # after
            self.final_result = self.azure_voice_processed


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

class AzureVoiceController():
    
    def __init__(self, quote):
        self.quote = quote
        if quote['deck__audio_enabled']:
            self.AzureVoiceIn = AzureVoice(self.quote)
            # Azure voice quote 
            self.voice_processed_quote = self.AzureVoiceIn.finished_voiced_quote
            # upload to s3
            self.UploadS3In = UploadS3(self.voice_processed_quote)
            # final returned dict 
            self.azure_voice_processed_quote= self.UploadS3In.finished_uploaded_quote
            print(self.azure_voice_processed_quote)
        else:
            # May need to approach difference between failed upload and not wanted upload
            self.quote['upload_audio_success']= False
            self.azure_voice_processed_quote = self.quote

class AzureVoice():
    
    def __init__(self, quote):
        # build audio config
        self.quote_with_codes = self.set_config(quote)
        self.quote_with_xml_file = self.create_xml(self.quote_with_codes)
        self.finished_voiced_quote = self.request_voice(self.quote_with_xml_file)
        # print(self.finished_voiced_quote)
    
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
            print('******ERROR IN SET_CONFIG OF AZURE VOICE*******')
            print('***********************************************')
        return quote

    
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
        quote['xml_filename'] = "code/forge/recycled_xml_for_api.xml"
        voice_data = ElementTree.tostring(speak)
        voice_file=open(quote['xml_filename'], "wb")
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
        quote['local_file_path']= f"code/forge/audio/{quote['universal_filename']}"
        self.stream.save_to_wav_file(quote['local_file_path'])
        return quote

    def create_universal_filename(self, quote):
        # This needs to be looked at for scale use this link
        # https://stackoverflow.com/questions/47529120/save-sentence-as-server-filename
        # https://stackoverflow.com/questions/3006710/python-unhash-value
        # self.simplified_quote = quote['voiced_quote'].translate({ord(c): None for c in string.whitespace})
        # hashing should be fine aslong as I dont lose ArchivedDB
        self.hashed_quote = hash(quote['voiced_quote'])
        quote['universal_filename'] = f"{self.hashed_quote}.mp3"
        return quote

class UploadS3():
    
    def __init__(self, quote):
        self.s3 = boto3.client('s3', aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
        # upload to s3
        self.finished_uploaded_quote = self.upload_to_s3(quote)
        # return location 
    
    def upload_to_s3(self, quote):
        # Create s3 file path
        quote['aws_file_path']= f"audio/{quote['voiced_quote_lang']}/{quote['universal_filename']}"
        # Save to file path, may need to allow for more errors
        try:
            self.s3.upload_file(quote['local_file_path'], os.environ['AWS_STORAGE_BUCKET_NAME'], quote['aws_file_path'])
            quote['upload_audio_success'] = True
        except FileNotFoundError:
            print("The file was not found")
            quote['upload_audio_success'] = False
        except NoCredentialsError:
            print("Credentials not available")
            quote['upload_audio_success'] = False    
        # return with dictionary file path
        return quote