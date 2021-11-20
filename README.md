# AnkiForge
## AnkiForge - Web based app to create media enriched Anki cards easily.
 Ankiforge.com is a web app that allows you to automatically make language learning Anki flashcards in up to 7 languages (Spanish, Italian, French, German, Japanese and Chinese x 2), from any device with a browser. Using English as the base language, AnkiForge will automatically translate any quote between the two desired languages, get synthesised speech (Azure neural voices) for the learnt language and find a relevant image. It will then format the card into your choice of mobile-ready Anki card styles - ready to be downloaded as .apkg files and used in Anki to speed up your language learning.
 
 #### Video demonstration of AnkiForge
 https://www.youtube.com/watch?v=nTL_rWi2_Ic&ab_channel=AnkiForge.
 
 ### Intent

I made this site my first real long term project and as a learning exercise. I had the intent to host it myself and allow others to use it. Due to this, it is built with authentication, stripe payment systems and subscriptions etc. However, after a long time working on and finally deploying it, other things got in the way and I no longer have the time to maintain it in a way that customers could use it.

## Tech
The website and desktop app is using the following tech: Django, Django Rest Framework, PostgreSQL, Celery, Docker, Redis, Electron, Stripe Payment Systems, Bootstrap, AWS S3.

## Synopsis for process
The user creates decks, which contain information of language learnt etc, this is saved in the `decks` model. When a user creates a new card, this is registered as an object in the `incomingCards` model. 
On save and with valid 'credit' remaining on the user account, a celery task is triggered. The bulk of logic for the translation, voice synthesis and image retrieval is found in this script, ran by celery `AnkiForge/Site/AnkiForge/AnkiForge/forge/MediaCollect.py`. In short, the process is this:

language detected and tagged, translation recorded and tagged with language. All done using googleCloudTranslation DB search of model `archivedCards` to see if media for this quote or language has already been found. If not, the quote in the learnt language is sent to Microsoft azure voice and synthesised speech is retrieved and uploaded to S3. For images, the English quote is reduced to just nouns if possible, to allow for better image searching. Azure search API is then used to retrieve the image of appropriate size and upload it to S3. The final result is an entry in the `archivedCards`model, which includes quotes in two languages, language tagged and media file addresses. 

When the user wishes to create an ankideck, media is collected from what was stored earlier. The task checks if these files are stored locally (will depend on which server the original task was sent to). If they are not, they will be downloaded from shared S3. The genanki package is then used to create `.apkg` Anki deck files. The '.apkg' file is then uploaded to S3 and a timed link is returned for the user to download the file.

Also, django rest frame work implemented so that users could authenticate and send cards from the electron desktop app. 

## Deployment

Deployment is designed to allow for horizontal scaling. One NGINX server routes request to multiple servers running the containerised Django app. All of the Django app containers then connect to a separate server running the PostgreSQL database. The branch used for this was `Layered_ProxyDjangoPostgreSQL`.

## Running

Full service with local DB can be run locally from the master branch, using the following commands.

`docker build --network=host -t testinstall2 .`

`docker tag testinstall2:latest testinstall:staging`

`docker-compose up`

However, will not function without addition of appropriate Azure, googletranslate and amazon s3 keys/accounts.
