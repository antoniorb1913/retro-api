#!/bin/bash

# 1. Captura variables para Cron
export > /opt/.env.sh
chmod 750 /opt/.env.sh

# 2. Esperar a la base de datos
echo "Esperando a la base de datos..."
while ! nc -z retro_db 5432; do
  sleep 0.5
done

# 3. Tareas de Django
cd /app
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# 4. Iniciar Cron
service cron start

echo "Arrancando Gunicorn con mi nombre personalizado..."
exec gunicorn -c servidor_config.py retro_inventary.wsgi