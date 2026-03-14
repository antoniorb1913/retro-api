FROM python:3.12-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Madrid

# Instalación de dependencias del sistema
# Se añade python3-dev y dos2unix para evitar errores de compilación y de formato
RUN apt-get update && apt-get install -qq -y \
    libpq-dev \
    gcc \
    python3-dev \
    cron \
    netcat-openbsd \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalamos las dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Configuración de Cron
COPY docker/cron/retro_cron /etc/cron.d/retro_cron
RUN chmod 0644 /etc/cron.d/retro_cron && crontab /etc/cron.d/retro_cron

# Copiamos scripts de utilidad y corregimos formato (por si vienen de Windows)
COPY docker/opt/ /opt/
RUN dos2unix /opt/*.sh && chmod +x /opt/*.sh

# Copiamos el resto del proyecto
COPY . /app/

# El entrypoint es el encargado de esperar a la DB y lanzar migraciones
ENTRYPOINT ["/opt/entrypoint.sh"]