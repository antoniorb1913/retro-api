FROM python:3.12-slim

# Evita archivos .pyc y asegura que los logs salgan directos a la consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Madrid

# 1. Dependencias del sistema (Agrupadas y con limpieza de caché para ahorrar espacio)
RUN apt-get update && apt-get install -qq -y \
    libpq-dev \
    gcc \
    python3-dev \
    cron \
    netcat-openbsd \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Gestión de Dependencias Python
# Copiamos primero solo los requisitos para aprovechar la caché de Docker
COPY requirements.txt requirements-dev.txt /app/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-dev.txt

# 3. Configuración de CRON (Blindaje de permisos)
# Copiamos el archivo de tareas programadas
COPY docker/cron /etc/cron.d/retro_cron

# Aplicamos limpieza de Windows, permisos estrictos (0644) y registro en el sistema
RUN dos2unix /etc/cron.d/retro_cron && \
    chmod 0644 /etc/cron.d/retro_cron && \
    # Aseguramos una línea vacía al final (requisito de Cron en Linux)
    echo "" >> /etc/cron.d/retro_cron && \
    crontab /etc/cron.d/retro_cron

# 4. Configuración de Scripts de Operación (/opt)
COPY docker/opt/ /opt/
# Curamos los scripts de posibles errores de formato Windows (\r)
RUN dos2unix /opt/*.sh && \
    chmod +x /opt/*.sh && \
    sed -i 's/\r$//' /opt/*.sh

# 5. Código Fuente
# Copiamos el resto del proyecto al final para que los cambios de código no obliguen a reinstalar librerías
COPY . /app/

# Lanzador maestro
ENTRYPOINT ["/bin/bash", "/opt/entrypoint.sh"]