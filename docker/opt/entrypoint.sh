#!/bin/bash

# 1. Preparación de variables (Limpieza de formato Windows \r)
export | sed 's/\r$//' > /opt/.env.sh
chmod 750 /opt/.env.sh

# 2. Espera activa a la Base de Datos
echo "⏳ Esperando a que la base de datos esté lista..."
while ! nc -z db 5432; do
  sleep 0.5
done
echo "✅ Base de datos conectada."

# 3. Operaciones de Django
cd /app

echo "🛠️ Ejecutando tareas de mantenimiento..."

# A) Migraciones automáticas
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# B) Superusuario Automático (Versión Inteligente)
if [ "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "👤 Configurando superusuario: $DJANGO_SUPERUSER_USERNAME..."
    python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
username = '$DJANGO_SUPERUSER_USERNAME'
email = '$DJANGO_SUPERUSER_EMAIL'
password = '$DJANGO_SUPERUSER_PASSWORD'

# Buscamos al usuario o lo creamos
user, created = User.objects.get_or_create(username=username)

if created:
    user.set_password(password)
    user.email = email
    print(f'✅ Usuario "{username}" creado desde cero.')
else:
    print(f'ℹ️ El usuario "{username}" ya existía, actualizando permisos...')

# FORZAMOS los permisos de administración siempre
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.save()
print(f'Acceso al Admin garantizado para "{username}".')
EOF
fi

# C) Gestión de archivos estáticos
echo "Actualizando archivos estáticos..."
rm -rf /app/staticfiles/*
python manage.py collectstatic --noinput

# 4. Servicios secundarios
echo "Arrancando Cron..."
service cron start

# 5. Ejecución final
if [ "$DEBUG" = "True" ]; then
    echo "MODO DESARROLLO: Servidor con autoreload activo."
    exec python manage.py runserver 0.0.0.0:8000
else
    echo "MODO PRODUCCIÓN: Servidor Gunicorn activo."
    exec gunicorn -c servidor_config.py retro_inventary.wsgi
fi