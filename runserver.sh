#!/usr/bin/env bash

if [[ "$SHELL" == *"fish"* ]]; then
    source env/bin/activate.fish
else
    source env/bin/activate
fi

# start server
cd fly_project
python manage.py runserver


# aguante riveeeeeeer