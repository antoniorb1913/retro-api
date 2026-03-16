FROM python:3.12-slim

# Evita archivos .pyc y asegura que los logs salgan directos a la consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Madrid

# 1. Dependencias del sistema
RUN apt-get update && apt-get install -qq -y \
    libpq-dev \
    gcc \
    python3-dev \
    cron \
    netcat-openbsd \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

    
WORKDIR /app

# 1. Copiamos AMBOS archivos de requisitos
COPY requirements.txt requirements-dev.txt /app/

# 2. Instalamos directamente el de desarrollo
# Al tener el "-r requirements.txt" dentro, instalará TODO de un tirón
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-dev.txt

# 3. Resto de la configuración (Cron, opt, etc.)
COPY docker/cron /etc/cron.d/retro_cron
RUN echo "" >> /etc/cron.d/retro_cron && \
    dos2unix /etc/cron.d/retro_cron && \
    chmod 0644 /etc/cron.d/retro_cron && \
    crontab /etc/cron.d/retro_cron

COPY docker/opt/ /opt/
RUN dos2unix /opt/*.sh && chmod +x /opt/*.sh && sed -i 's/\r$//' /opt/*.sh

COPY . /app/

ENTRYPOINT ["/bin/bash", "/opt/entrypoint.sh"]