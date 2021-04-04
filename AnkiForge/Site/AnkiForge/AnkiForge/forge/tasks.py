from celery import shared_task
from decks.models import IncomingCards, ArchivedCards, ForgedDecks, MediaTransactions, CardModels, UserDecks
from celery.decorators import task
from celery.utils.log import get_task_logger
from forge.MediaCollect import Controller
from celery_progress.backend import ProgressRecorder
import time
import genanki
from forge.DeckModels import *
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import os
import logging
from botocore.client import Config


logger = get_task_logger(__name__)

# Potentially change this to async task where can send query as argument (maybe even dict it first).
#  NEED TO LOOK INTO HOW THIS WILL WORK WITH MULTIPLE WORKERS

"""MEDIA COLLECT ON INVOMCING CARD SAVE"""
@shared_task(name='translate_and_archive')
def translate_and_archive(new_item):
    quotes = IncomingCards.readyforprocess_objects.filter(id=new_item).values(
        'id','user_id','deck_id','deck__learnt_lang',
        'deck__native_lang','deck__images_enabled',
        'deck__audio_enabled','incoming_quote'
        ) 
    translated_result = False
    for quote in quotes:   
        processed = Controller(quote)
        print(processed.final_result)
        final_result = (processed.final_result)
    # Check that translation worked
    if final_result:
        if final_result['audio_found_in_db'] and final_result['image_found_in_db']:
            save_with_db_media(final_result)
            print(f"***INCOMING CARD SAVED WITH PREVIOUS ARCHIVED CARD ID = {final_result['archived_card_id']}***")
        else:
            save_with_retrieved_media(final_result)
    else :
        print("***FAILURE IN MEDIA_COLLECT.PY TO RETURN RESULT**")

def save_with_db_media(final_result):
    archived_object = ArchivedCards.objects.get(id = final_result['archived_card_id'])
    updated_quote = update_incomingcards(final_result, archived_object)
    make_mediatransactions(final_result, updated_quote)

def save_with_retrieved_media(final_result):    
    archived_object = make_archivedcards(final_result)                      # Make archived
    updated_quote = update_incomingcards(final_result, archived_object)    #Updated incoming card
    make_mediatransactions(final_result, updated_quote) 

def make_archivedcards(final_result):
        archived_object = ArchivedCards(
            original_quote = final_result['incoming_quote'],
            original_language = final_result['original_language'],
            translated_quote = final_result['translated_quote'],
            translated_language = final_result['translated_language'],
        )
        if final_result['deck__audio_enabled']:
            archived_object.aws_audio_file_path = final_result['aws_audio_file_path']
            archived_object.local_audio_file_path = final_result['local_file_path']
            archived_object.universal_audio_filename= final_result['universal_audio_filename']
            archived_object.upload_audio_success= final_result['upload_audio_success']
            archived_object.voiced_quote= final_result['voiced_quote']
            archived_object.voiced_quote_lang= final_result['voiced_quote_lang']
        if final_result['deck__images_enabled']:
            archived_object.aws_image_file_path=final_result['aws_image_file_path']
            archived_object.local_image_file_path = final_result['local_image_filepath']
            archived_object.universal_image_filename=final_result['universal_image_filename']
            archived_object.upload_image_success=final_result['upload_image_success']
            archived_object.image_search_phrase_string=final_result['image_search_phrase_string']
            archived_object.retrieved_image_url= final_result['retrieved_image_url']
        archived_object.save()
        return archived_object

def update_incomingcards(final_result, archived_object):
        updated_quote = IncomingCards.objects.get(id=final_result['id'])
        updated_quote.ready_for_archive = False
        updated_quote.submitted_to_archive=True
        updated_quote.archived_card = archived_object
        updated_quote.save()
        return updated_quote
 
def make_mediatransactions(final_result, updated_quote):
        transaction_object = MediaTransactions( 
            incoming_card = updated_quote,
            charecters_sent_translator = len(final_result['incoming_quote']),
            charecters_returned_translator = len(final_result['translated_quote']),
            charecters_sent_detect = len(final_result['detection_quote']),
            audio_enabled = final_result['deck__audio_enabled'],
            media_enabled =final_result['deck__images_enabled'],
        )
        if final_result['deck__audio_enabled']:
            transaction_object.voiced_quote_lang=final_result['voiced_quote_lang']
            transaction_object.audio_found_in_db=final_result['audio_found_in_db']
            if final_result['audio_found_in_db']:
                pass
            else: 
                transaction_object.characters_sent_azure_voice= len(final_result['voiced_quote'])
        if final_result['deck__images_enabled']:
            transaction_object.image_found_in_db=final_result['image_found_in_db']
        transaction_object.save()

""" FORGING DECKS TASK """


@shared_task(bind=True, name='forge_deck')
def forge_deck(self, deck, user):
    progress_recorder =ProgressRecorder(self)
    progress = 0
    deck_to_forge = IncomingCards.readyforforge.filter(deck = deck, user = user)
    cards = deck_to_forge.values(
        'id', 'archived_card__original_quote',
        'user',
        'archived_card__original_language',
        'archived_card__translated_quote',
        'archived_card__translated_language',
        'deck__id',
        'deck__learnt_lang', 'deck__native_lang',
        'deck__images_enabled', 'deck__audio_enabled',
        'deck__model_code__model_name', 'deck__deck_id', 'deck__anki_deck_name',
        'archived_card__local_audio_file_path',
        'archived_card__local_image_file_path',
        'archived_card__upload_audio_success',
        'archived_card__upload_image_success',
        'archived_card__aws_audio_file_path',
        'archived_card__aws_image_file_path',
        'archived_card__universal_audio_filename',
        'archived_card__universal_image_filename',
    )
    # set progress settings
    max_progress = 100
    progress_unit = 20
    print(cards[0])
    progress_recorder.set_progress(progress, max_progress)
    cards_assigned_language = assign_language(cards)
    deck_made, progress_recorder, progress = make_deck(cards_assigned_language, progress_recorder, progress, max_progress)
    # set progress after make file
    progress+=progress_unit
    progress_recorder.set_progress(progress, max_progress)
    # set progress after make file
    s3 = boto3.client('s3',
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        config=Config(
            signature_version='s3v4',
            region_name = 'us-east-2'
            ))
    uploaded = upload_deck_to_s3(deck_made, s3)
    # set progress after upload
    progress+=progress_unit
    progress_recorder.set_progress(progress, max_progress)
    # progress set after upload
    uploaded_with_download = get_download_link(cards, s3)
    # set progress after creating link
    progress+=progress_unit
    progress_recorder.set_progress(progress, max_progress)
    # set progress after creating link
    forged_deck_object = create_forgeddecks(uploaded_with_download)
    update_incoming_cards_forge(forged_deck_object, uploaded_with_download)
    # final set progress
    progress+=progress_unit
    progress_recorder.set_progress(progress, max_progress)
    # final set progress
    return uploaded_with_download[0]['aws_download_link']
    



# @shared_task(bind=True, name='forge_deck')
# def forge_deck(self, seconds, pk):
#     progress_recorder = ProgressRecorder(self)
#     result = 0
#     for i in range(seconds):
#         time.sleep(1)
#         result += i
#         progress_recorder.set_progress(i + 1, 100)
#     return pk

def assign_language(cards):
    # handed a iterable query set
    processed_cards = []
    print(cards[0])
    for card in cards:
        if card['deck__learnt_lang'][:2]==card['archived_card__original_language'][:2]:
            card['learnt_quote'] = card['archived_card__original_quote']
            card['native_quote']= card['archived_card__translated_quote']
            processed_cards.append(card)
        elif card['deck__learnt_lang'][:2]==card['archived_card__translated_language'][:2]:
            card['learnt_quote'] = card['archived_card__translated_quote']
            card['native_quote']= card['archived_card__original_quote']
            processed_cards.append(card)
        else: 
            print("*** FAILED TO ASSIGN LANGUAGE ***")
    return processed_cards

def make_deck(cards, progress_recorder, progress, max_progress):
    if not cards:
        pass
    else:
        progress_unit = 20/len(cards)
        cards = make_deck_filename(cards)
        deck_media_files = []
        deck = genanki.Deck(
            cards[0]['deck__deck_id'],
            cards[0]['deck__anki_deck_name']
        )
        # little benefit lot of work to be able to retrieve and format model code from db
        model_instance = convert_instance(cards[0]['deck__model_code__model_name'])
        model = genanki.Model(
            cards[0]['deck__deck_id'],
            model_instance.model_name,
            css=model_instance.css,
            fields=model_instance.fields,
            templates=model_instance.templates)
        for card in cards:
            # (filepath, filename)
            # [[x['input'], x['translatedText']] for x in results]
            # first one is english native second is learnt
            if card['deck__audio_enabled']:
                deck_media_files.append(card['archived_card__local_audio_file_path'])
            if card['deck__images_enabled']:
                deck_media_files.append(card['archived_card__local_image_file_path'])
            image_filename = card['archived_card__universal_image_filename']
            audio_filename = card['archived_card__universal_audio_filename']
            capitalised_native_quote = card["native_quote"][0].upper() + card["native_quote"][1:]
            capitalised_learnt_quote = card["learnt_quote"][0].upper() + card["learnt_quote"][1:]
            # check that we have the media trying to attach
            if image_filename and audio_filename:
                print("*ITS TRYING THIS*")
                note = genanki.Note(
                    model = model,
                    fields = [
                        f'{capitalised_native_quote}',
                        f'{capitalised_learnt_quote}',
                        f'<img src="{image_filename}">',
                        f'[sound:{audio_filename}]'
                    ]
                )
            elif audio_filename:
                print("*ITS TRYING THIS 2*")
                note = genanki.Note(
                    model = model,
                    fields = [
                        f'{capitalised_native_quote}',
                        f'{capitalised_learnt_quote}',
                        f'[sound:{audio_filename}]'
                    ]
                )
            elif image_filename:
                print("*ITS TRYING THIS 3*")
                note = genanki.Note(
                    model = model,
                    fields = [
                        f'{capitalised_native_quote}',
                        f'{capitalised_learnt_quote}',
                        f'<img src="{image_filename}">',
                    ]
                )
            else: 
                note = genanki.Note(
                    model = model,
                    fields = [
                        f'{capitalised_native_quote}',
                        f'{capitalised_learnt_quote}',
                    ]
                )  
            deck.add_note(note)
            # record progress
            progress+=progress_unit
            progress_recorder.set_progress(progress, max_progress)
        package = genanki.Package(deck)
        package.media_files = deck_media_files
        print(f'{cards[0]["deck_local_filepath"]}')
        package.write_to_file(f'{cards[0]["deck_local_filepath"]}')
        return cards, progress_recorder, progress


def convert_instance(model_name):
    # Max like 6 models, worth just setting it like this and having long code in another file

    if model_name == 'Standard': 
        model = StandardModel()
        return model
    elif model_name == 'PrettyStandardModel':
        model = PrettyStandardModel()
        return model
    elif model_name == 'PrettyStandardModelTextBothSides':
        model = PrettyStandardModelTextBothSides()
        return model
    elif model_name =='PrettyStandardModelNoImage':
        model = PrettyStandardModelNoImage
        return model
    elif model_name == 'PrettyStandardModelNoAudio':
        model = PrettyStandardModelNoAudio
        return model
    else: 
        print:"HERES YOUR FUCK UP"

def make_deck_filename(cards):
    card_ids = [card['id'] for card in cards]
    cards_processed = f'{min(card_ids)}-{max(card_ids)}'
    filename = f'{cards[0]["user"]}-{cards[0]["deck__id"]}-{cards_processed}.apkg'
    local_filepath = f'forge/forgeddecks/{filename}'
    print(f"*LOCAL FILENAME ={local_filepath}*")
    aws_filepath = f'forgeddecks/{filename}'
    for card in cards:
        card['deck_local_filepath'] = local_filepath
        card['deck_aws_filepath'] = aws_filepath
        card['deck_filename'] = filename
    return cards

def create_forgeddecks(cards):
    deck = UserDecks.objects.get(id=cards[0]['deck__id'])
    forged_deck_object = ForgedDecks(
        aws_file_path = cards[0]['deck_aws_filepath'],
        aws_download_link = cards[0]['aws_download_link'],
        local_file_path = cards[0]['deck_local_filepath'],
        deck_filename = cards[0]['deck_filename'],
        deck = deck,
        number_of_cards = len(cards)
    )
    forged_deck_object.save()
    return forged_deck_object

def update_incoming_cards_forge(forged_deck_object, cards):
    for card in cards:
        updated_quote = IncomingCards.objects.get(id=card['id'])
        # Usefulf for debugging to not change this each time
        updated_quote.deck_made = True
        updated_quote.forged_deck = forged_deck_object
        updated_quote.save()

def upload_deck_to_s3(cards, s3):
    print("*UPLOADING DECK TO S3")
    try:
        s3.upload_file(cards[0]['deck_local_filepath'], os.environ['AWS_STORAGE_BUCKET_NAME'], cards[0]['deck_aws_filepath'])
        cards[0]['upload_deck_success'] = True
        print('*DECK UPLOADED*')
    except FileNotFoundError:
        print("The file was not found")
        cards[0]['upload_deck_success'] = False
    except NoCredentialsError:
        print("Credentials not available")
        cards[0]['upload_deck_success'] = False
    return cards


def get_download_link(cards, s3):
    print("*MAKING DOWNLOAD LINK*")
    try:
        response = s3.generate_presigned_url('get_object',
                                                    Params={'Bucket': os.environ['AWS_STORAGE_BUCKET_NAME'],
                                                            'Key': cards[0]['deck_aws_filepath']},
                                                    ExpiresIn=600)
        print(f"*GENERATED PRESIGNED URL AT {response}  *")
        cards[0]['aws_download_link'] = response
    except ClientError as e:
        logging.error(e)
    
    return cards