#!/usr/bin/env bash

if [[ "$SHELL" == *"fish"* ]]; then
    source .venv/bin/activate.fish
else
    source .venv/bin/activate
fi

# start server
cd fly_project
python manage.py runserver


# aguante riveeeeeeer