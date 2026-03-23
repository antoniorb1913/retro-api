# 5. Base de Datos (Conectada al contenedor 'db' vía .env)
from .base import *

# Convertimos el String "True" del .env a un Booleano real de Python
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Tomamos los hosts del .env y los convertimos en una lista
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

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