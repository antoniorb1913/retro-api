import os
from pathlib import Path

# 1. Rutas Base
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# 2. Seguridad (Configuración Dinámica desde .env)
# Si no encuentra la variable en el .env, usa un valor de seguridad por defecto
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-change-me')

# Convertimos el String "True" del .env a un Booleano real de Python
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Tomamos los hosts del .env y los convertimos en una lista
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

# 3. Aplicaciones
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'import_export',
    'apps', # Tu aplicación de inventario
]

# 4. Middleware (Configuración con Whitenoise para Estáticos)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Debe ir justo debajo de SecurityMiddleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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

# 6. Internacionalización
LANGUAGE_CODE = 'es'
TIME_ZONE = os.environ.get('TZ', 'Europe/Madrid') # Sincronizado con el contenedor
USE_I18N = True
USE_TZ = True

# 7. Archivos Estáticos (Configuración Robusta para Docker)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Carpeta donde pondrás tus CSS/JS personalizados
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Almacenamiento optimizado para servir archivos sin errores de tamaño 0
STATICFILES_STORAGE = 'whitenoise.storage.StaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Opcional: Desactivar la barra lateral del admin si prefieres el look clásico
# admin.site.enable_nav_sidebar = False