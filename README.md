# AnkiForge
## AnkiForge - Web based app to create media enriched Anki cards easily.
 Ankiforge.com is a web app that allows you to automatically make language learning Anki flashcards in up to 7 languages (Spanish, Italian, French, German, Japanese and Chinese x 2), from any device with a browser. Using English as the base language, AnkiForge will automatically translate any quote between the two desired languages, get synthesised speech (Azure neural voices) for the learnt language and find a relevant image. It will then format the card into your choice of mobile-ready Anki card styles - ready to be downloaded as .apkg files and used in Anki to speed up your language learning.
 
 #### Video demonstration of AnkiForge
 https://www.youtube.com/watch?v=nTL_rWi2_Ic&ab_channel=AnkiForge.
 
 ## Intent

I made this site as a my first real long term project. I had the intent to host it myself and allow others to use it. Due to this it is built with authentication, stripe payment systems and subscriptions etc. However, after 9 months working on it and just after finishing and deploying it, I got a job. I no longer have time to maintain the site and commit to running it for customers. So after leaving it un-touched for four months, I'm going to make it open source.

## Tech
The is website and desktop app is using the following tech: Django, Django Rest Framework, PostgreSQL, Celery, Docker, Redis, Electron, Stripe Payment Systems, Bootstrap, AWS S3.

## Synopsis for process
User creates decks, which contain information of language learnt etc, this is saved in the `decks` model. When a user creates a new card, this is registered as an object in `incomingCards` model. 
On save and with valid 'credit' remaining on the user account, a celery task is triggered. The bulk of logic for the translation, voice synthesis and image retrieval is found in this script, ran by celery `AnkiForge/Site/AnkiForge/AnkiForge/forge/MediaCollect.py`. In short, the process is this:

language detected and tagged, translation recorded and tagged with language. All done using googleCloudTranslation DB search of model `archivedCards` to see if media for this quote or language has already been found. If not, the quote in learnt language is sent to microsoft azure voice and synthesised speech is retrieved and uploaded to S3. For images, the English quote is reduced to just nouns if possible, to allow for better image searching. Azure search API then used to retrieve image of appropriate size and uploaded to S3. The final result is an entry in the `archivedCards`model, that includes quote, language and media file addresses. 

When the user wishes to create an ankideck, the genanki package is used and the media is collected from what was stored earlier. The '.apkg' file is then uploaded to S3 and a timed link is returned for the user to download the file.

Also set up with django rest frame work so that user could authenticate and send cards from electron desktop app. 

## How to run

in ``
