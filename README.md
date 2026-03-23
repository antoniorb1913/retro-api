# Instalación del proyecto API.

## Tener instalado Python, Django, Django REST, 



## Para crear un super usuario en django 
docker exec -it retro_app python manage.py createsuperuser


migrations
docker exec -it retro_app python manage.py makemigrations --settings=retro_inventary.local

migrate
docker exec -it retro_app python manage.py migrate --settings=retro_inventary.local