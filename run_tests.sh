#!/usr/bin/env bash

# Script para correr tests unitarios y de integración de Django

set -e

cd "$(dirname "$0")/fly_project"

echo "Ejecutando tests unitarios (app/tests.py)..."
python manage.py test app

echo "Ejecutando tests de integración (api/tests.py)..."
python manage.py test api

echo "Todos los tests finalizados."
