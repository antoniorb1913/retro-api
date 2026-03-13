#!/bin/bash

echo "--- Esperando a la base de datos y aplicando migraciones ---"
python manage.py migrate --noinput

echo "--- Iniciando servidor de Django ---"
python manage.py runserver 0.0.0.0:8000
