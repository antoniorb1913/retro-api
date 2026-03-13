FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Madrid

RUN apt-get update && apt-get install -qq -y \
    libpq-dev \
    gcc \
    cron \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY docker/cron/retro_cron /etc/cron.d/retro_cron
RUN chmod 0644 /etc/cron.d/retro_cron && crontab /etc/cron.d/retro_cron

COPY docker/opt/ /opt/
RUN chmod +x /opt/*.sh

COPY . /app/

ENTRYPOINT ["/opt/entrypoint.sh"]