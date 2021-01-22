#!/bin/sh
sleep 1
python3.6 manage.py makemigrations
python3.6 manage.py migrate
python3.6 manage.py loaddata StartUpFiles/DecksDump.json
python3.6 manage.py loaddata StartUpFiles/MembershipDump.json
python3.6 manage.py runserver 0.0.0.0:8000

exec "$@"
