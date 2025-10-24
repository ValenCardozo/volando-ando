#!/usr/bin/env bash

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

if [[ "$SHELL" == *"fish"* ]]; then
    source .venv/bin/activate.fish
else
    source .venv/bin/activate
fi

# dependencias
pip install -r requeriments.txt

# Migraciones y seeders
cd fly_project
python manage.py migrate
python manage.py dbshell < seeds/seed_arg_airline.sql
python manage.py dbshell < seeds/seed_destinations.sql
cd ..

echo "Setup completo. Puedes iniciar el servidor con ./runserver.sh"

# aguante riveeeeeeer