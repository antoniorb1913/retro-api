import os
from pathlib import Path

# 1. Rutas Base
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. Seguridad
SECRET_KEY = 'django-insecure-1_38!xshj&6p^=a4o2+uschg#$wqfhs31!nj(9)y63*o!%s*b1'
DEBUG = True
ALLOWED_HOSTS = ['*']  # Necesario para que Docker funcione

# 3. Aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'import_export',
    'apps', # Tu aplicación de inventario
]

# 4. Middleware (Limpio, sin Whitenoise para evitar fallos de diseño)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'retro_inventary.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'retro_inventary.wsgi.application'

# 5. Base de Datos (Configurada para el contenedor 'db' de tu docker-compose)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'retro_db',
        'USER': 'admin',
        'PASSWORD': 'postgres',
        'HOST': 'db',
        'PORT': '5432',
    }
}

# 6. Internacionalización
LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 7. Archivos Estáticos (Configuración Robusta para runserver)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Importante: Corchetes [] para evitar el error E001
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
