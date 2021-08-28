# AnkiForge
## AnkiForge - Web based app to create media enriched Anki cards easily.
 Ankiforge.com is a web app that allows you to automatically make language learning Anki flashcards in up to 7 languages (Spanish, Italian, French, German, Japanese and Chinese x 2), from any device with a browser. Using English as the base language, AnkiForge will automatically translate any quote between the two desired languages, get synthesised speech (Azure neural voices) for the learnt language and find a relevant image. It will then format the card into your choice of mobile-ready Anki card styles - ready to be downloaded as .apkg files and used in Anki to speed up your language learning.
 
 #### Video demonstration of AnkiForge
 https://www.youtube.com/watch?v=nTL_rWi2_Ic&ab_channel=AnkiForge.
 
 ## Intent

I orignally made this site with intent to host it myself and allow others to use it. However, after 9 months working on it and just finishing it, I got a job. I no longer have time to maintain the site and commit to running it for customers. So after leaving it un-touched for four months, I've decided to make it open source incase anyone wants to have a go at it.

## Tech
The is website and desktop app is using the following tech: Django, Django Rest Framework, PostgreSQL, Celery, Docker, Redis, Electron, Stripe Payment Systems, Bootstrap, AWS S3.

The bulk of logic for translation, voice synthesis and media is found in this script, ran by celery `AnkiForge/Site/AnkiForge/AnkiForge/forge/MediaCollect.py`. 
