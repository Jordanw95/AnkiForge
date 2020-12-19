#!/bin/sh
sleep 1
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata StartUpFiles/DecksDump.json
python manage.py loaddata StartUpFiles/MembershipDump.json
python manage.py runserver 0.0.0.0:8000

exec "$@"
