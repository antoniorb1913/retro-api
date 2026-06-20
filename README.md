# 🎮 Retro Inventory API

Una API REST profesional y altamente optimizada desarrollada con **Django** y **Django REST Framework (DRF)** para la gestión y catalogación de colecciones e inventarios de videojuegos, consolas y accesorios retro. 

El proyecto cuenta con una arquitectura robusta, relaciones polimórficas eficientes para el manejo de imágenes multimedia, filtros avanzados de búsqueda y ordenación, autenticación segura mediante **JWT (JSON Web Tokens)**, y está completamente contenerizado utilizando **Docker** y **Docker Compose** para un despliegue inmediato.

---


## 🛠️ Stack Tecnológico

* **Backend:** Python 3 / Django / Django REST Framework (DRF)
* **Autenticación:** Spectacular JWT (JSON Web Tokens)
* **Contenedores y Despliegue:** Docker / Docker Compose
* **Herramientas de Desarrollo:** Git, WSL 2 (Windows Subsystem for Linux)

---

## 📦 Estructura de Endpoints Clave (`/api/v1/`)

El enrutador automático (`DefaultRouter`) expone los siguientes endpoints estandarizados:

* `GET / POST` `/api/v1/consoles/` - Listar y crear consolas retro.
* `GET / PUT / DELETE` `/api/v1/consoles/<id>/` - Detalle, edición y borrado de una consola.
* `GET / POST` `/api/v1/games/` - Listar y crear videojuegos.
* `GET / PUT / DELETE` `/api/v1/games/<id>/` - Detalle, edición y borrado de un videojuego.
* `GET / POST` `/api/v1/accessories/` - Listar y crear accesorios.
* `GET / POST` `/api/v1/missing-components/` - Gestión de componentes faltantes (cajas, manuales, tapas...).
* `GET / POST / DELETE` `/api/v1/images/` - Subida (`multipart/form-data`) y lectura limpia de imágenes.

### Parámetros de Query Avanzados
* **Búsqueda:** `/api/v1/games/?search=Zelda` (Busca en nombre, modelo, plataforma o región).
* **Ordenación:** `/api/v1/consoles/?ordering=-price` (Ordena de mayor a menor precio).

---

## ⚙️ Requisitos Previos

Antes de arrancar el proyecto, asegúrate de tener instalado en tu sistema:
1. [Docker](https://docs.docker.com/get-docker/)
2. [Docker Compose](https://docs.docker.com/compose/install/)
3. Git (si usas Windows, se recomienda realizar las operaciones desde la terminal de **WSL 2**).

---

## 🏁 Cómo Arrancar el Proyecto

Sigue estos sencillos pasos para clonar y poner en marcha el backend en tu entorno local:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/antoniorb1913/retro-api.git](https://github.com/antoniorb1913/retro-api.git)

cd retro-api
```

### 2. Clonar el repositorio

Crea un archivo .env en la raíz del proyecto para definir las credenciales seguras (este archivo está configurado en tu .gitignore para que nunca se suba públicamente):

```bash
touch .env
```
Añade la configuración de tu entorno, por ejemplo:

```bash
DEBUG=True
SECRET_KEY=tu_clave_secreta_super_segura_de_django
DB_NAME=retro_db
DB_USER=retro_user
DB_PASSWORD=retro_password
DB_HOST=db
DB_PORT=5432
```

### 3. Levantar los Contenedores con Docker Compose

Este comando descargará las imágenes necesarias, configurará los volúmenes, la base de datos y encenderá el servidor de desarrollo de Django:

```bash
docker compose up --build
```

### 4. Ejecutar Migraciones de Base de Datos

En una nueva pestaña de la terminal, aplica las migraciones para estructurar las tablas en la base de datos:

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

### 5. Crear un Superusuario (Administrador)

Para poder acceder al panel de administración de Django (/admin/) e interactuar con total control sobre los datos:

```bash
docker compose exec web python manage.py createsuperuser
```

## Acceso a la Aplicación

Una vez que los contenedores estén corriendo de manera exitosa:

 - API REST (Endpoints): Puedes consumirla o probarla en el navegador en http://localhost:8000/api/v1/.

 - Panel de Administración de Django: Disponible en http://localhost:8000/admin/.

## Comandos de Utilidad

 - Detener los contenedores: docker compose down

 - Ver los logs en tiempo real: docker compose logs -f

 - Reiniciar el servidor: docker compose restart web