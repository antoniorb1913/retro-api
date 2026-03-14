#!/bin/bash
set -e  # Esto detiene el script si algo falla

echo "--- Iniciando el servicio de Cron ---"
service cron start

echo "--- Esperando a la base de datos y aplicando migraciones ---"
# Opcional: añade un check de netcat aquí si falla la conexión inicial
python manage.py migrate --noinput

echo "--- Iniciando servidor de Django ---"
exec python manage.py runserver 0.0.0.0:8000