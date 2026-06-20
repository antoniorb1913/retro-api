# 1. Imagen base oficial de Python (ligera y estable)
FROM python:3.12-slim

# 2. Evita que Python escriba archivos .pyc en el disco (ahorra espacio)
ENV PYTHONDONTWRITEBYTECODE=1

# 3. Evita que Python guarde en búfer los outputs (así los errores se ven al instante en la consola)
ENV PYTHONUNBUFFERED=1

# 4. Define la carpeta de trabajo dentro del contenedor
WORKDIR /app

# 5. Instala las dependencias del sistema necesarias para compilar librerías como psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 6. Copia primero el archivo de requisitos para aprovechar la caché de Docker
COPY requirements.txt /app/

# 7. Actualiza pip e instala las librerías del proyecto
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 8. Copia todo el resto del código del proyecto dentro del contenedor
COPY . /app/