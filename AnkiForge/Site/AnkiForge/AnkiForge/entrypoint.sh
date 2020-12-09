#!/bin/sh
set -e
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata StartUpFiles/DecksDump.json
python manage.py loaddata StartUpFiles/MembershipDump.json

exec "$@"