# AGENTS.md — RETRO_INVENTARY

Documento **autoritativo** para cualquier agente de IA (o persona) que trabaje en el proyecto.
Cubre **los dos repositorios a la vez**: `retro-api` (backend) y `retro-app` (frontend).

> **Dónde vive este archivo.** Hay una copia en cada sitio, con el mismo contenido: la **raíz del
> espacio de trabajo** (la carpeta que contiene los dos repos, copia de trabajo), **`retro-api/AGENTS.md`**
> y **`retro-app/AGENTS.md`**. Las dos copias que están dentro de los repos son las que se versionan
> en Git, y son las que mandan.

> **Cómo leer las rutas.** Las rutas de este documento están escritas **desde la carpeta que contiene
> los dos repos** (el espacio de trabajo): por ejemplo `retro-api/core/settings.py`. Si trabajas
> dentro de un repo, quita el prefijo: `retro-api/core/settings.py` es `core/settings.py` dentro de
> `retro-api`, y `retro-app/src/...` es `src/...` dentro de `retro-app`.

> **Regla de sincronización (obligatoria).** Este documento existe en tres sitios. **Cualquier cambio
> se aplica a las tres copias en el mismo momento.** Después se comprueba que son idénticas
> (`md5sum AGENTS.md retro-api/AGENTS.md retro-app/AGENTS.md` debe dar el mismo hash en las tres);
> si alguna difiere, se copia la buena sobre las otras. Nunca se edita una sola copia.

> Estado: creado en **septiembre de 2026** tras leer ambos repos completos, y ampliado después con
> los estándares de entorno real (testing, transacciones, observabilidad, despliegue y onboarding).
> Si algo no coincide con el código real, **manda el código**: avisa y se actualiza este documento.
> Este archivo no contiene código ejecutable, solo reglas y contexto.

---

## 0. Cómo leer este documento (orden de prioridad)

Cuando haya conflicto entre fuentes, gana la de más arriba:

1. **Instrucción directa del humano** en la conversación (por encima de todo).
2. **Este `AGENTS.md`** (las reglas de este documento; hay una copia en cada repo y son las
   que se versionan).
3. `docs/PLAN.md` del listado de tareas en curso (estado y alcance de la tarea actual).
4. `retro-api/docs/history/` y `retro-app/docs/history/` (histórico de lo ya hecho y verificado).
5. `retro-api/README.md`, `retro-app/README.md`.
6. `retro-app/HISTORIAL.md` → histórico **antiguo**, se conserva solo como referencia; puede
   contener rutas y comandos obsoletos (habla de Jasmine/Karma, `/api/v1/`, `game-list.component.ts`).
   Los archivos `AGENTS.md` **no** entran en este orden de prioridad: son siempre este documento, y
   entre sus copias manda la que está dentro del repo (`retro-api/AGENTS.md`, `retro-app/AGENTS.md`).

Si detectas una contradicción, **párate y pregunta** antes de actuar.

---

## 1. Qué es RETRO_INVENTORY

Plataforma web para coleccionistas de videojuegos clásicos: cataloga **consolas, juegos y
accesorios retro**, con estado físico, precio, tienda de compra, región, componentes faltantes
(caja, manual, etc.) e imágenes (convertidas a WebP).

- **Backend**: API REST con Django + DRF, autenticación JWT, PostgreSQL, todo en Docker.
- **Frontend**: SPA Angular (standalone + signals) que consume esa API.

---

## 2. Los dos repositorios: mapa real de carpetas

### 2.1 `retro-api/` — backend (repo Git independiente)

> Las rutas de este mapa se leen desde el espacio de trabajo. Dentro del repo `retro-api`,
> `retro-api/core/` es `core/`.

```
retro-api/
├─ core/                      # Proyecto Django (configuración)
│  ├─ settings.py             # django-environ, JWT, CORS, DRF, spectacular, MEDIA
│  ├─ urls.py                 # admin + /api/ + schema/docs/redocs + media
│  ├─ asgi.py / wsgi.py
├─ user/                      # App de usuarios (custom user)
│  ├─ models.py               # User(AbstractUser), USERNAME_FIELD = 'email'
│  ├─ admin.py                # UserAdmin personalizado
│  ├─ api/
│  │  ├─ router.py            # /api/api/token/ y /api/api/token/refresh/
│  │  ├─ serializers.py       # UserRegisterSerializer
│  │  └─ views.py             # RegistroView (público)
│  └─ migrations/
├─ inventory/                 # App de inventario (núcleo del negocio)
│  ├─ models/
│  │  ├─ Base.py              # ItemBase (abstracto): choices + campos comunes
│  │  ├─ Console.py           # Console(ItemBase) + edition
│  │  ├─ Game.py              # Game(ItemBase) + edition
│  │  ├─ Accessory.py         # Accessory(ItemBase)
│  │  ├─ Missing_component.py # MissingComponent (name único)
│  │  └─ Image.py             # ItemImage (GenericForeignKey) + WebP + signals
│  ├─ api/
│  │  ├─ router.py            # DefaultRouter → consoles/games/accessories/images/components
│  │  ├─ serializers/         # un archivo por modelo (+ item_base.py, image.py)
│  │  └─ views/               # un ViewSet por recurso (view_<recurso>.py)
│  ├─ migrations/             # 0001 → 0014
│  ├─ admin.py                # Admin con ItemImageInline genérico
│  └─ tests.py, views.py
├─ media/                     # Archivos subidos (NO versionado, servido en /media/)
├─ Dockerfile                 # python:3.12-slim + gcc/libpq-dev + requirements
├─ docker-compose.yml         # servicios db (postgres:16) y api
├─ requirements.txt           # dependencias fijadas (versiones exactas)
├─ manage.py                  # entrypoint de Django
├─ .env                       # credenciales (gitignored) ← NO versionar
├─ backup.sql                 # volcado de datos (sin trackear en Git)
├─ restore_data.py            # script de restauración (sin trackear)
└─ verify.py                  # conteo rápido de registros (sin trackear)
```

### 2.2 `retro-app/` — frontend (repo Git independiente)

> Igual que arriba: dentro del repo `retro-app`, `retro-app/src/` es `src/`.

```
retro-app/
├─ src/
│  ├─ main.ts                 # bootstrapApplication(App, appConfig)
│  ├─ index.html, styles.scss # estilos globales retro
│  ├─ environments/
│  │  ├─ environment.ts               # producción (apiUrl)
│  │  └─ environment.development.ts   # desarrollo (fileReplacements)
│  └─ app/
│     ├─ app.component.ts|html # App raíz (solo <router-outlet />)
│     ├─ app.config.ts         # providers: router + httpClient + interceptor
│     ├─ app.routes.ts         # rutas raíz (login, layout protegido, lazy features)
│     ├─ core/                 # servicios y piezas globales (singleton)
│     │  ├─ api.service.ts             # CRUD genérico tipado
│     │  ├─ auth.service.ts            # JWT + signals
│     │  ├─ auth.interceptor.ts        # Bearer + refresh en 401
│     │  ├─ auth.guard.ts              # protección de rutas
│     │  ├─ layout.component.*         # shell con navegación
│     │  ├─ list-filter-state.service.ts  # recuerda los filtros de cada lista (en memoria)
│     │  └─ missing-component.service.ts
│     ├─ models/               # interfaces + enums (contrato con la API) + index.ts (barrel)
│     ├─ features/             # una carpeta por dominio
│     │  ├─ auth/login.component.*
│     │  ├─ dashboard/dashboard.component.*
│     │  ├─ consoles/  {console.service.ts, consoles.routes.ts, list/, detail/, form/}
│     │  ├─ games/     {game.service.ts, games.routes.ts, list/, detail/, form/}
│     │  └─ accessories/{accessory.service.ts, accessories.routes.ts, list/, detail/, form/}
│     └─ shared/               # reutilizable
│        ├─ image-upload/image-upload.component.*
│        └─ pagination/pagination.component.*
├─ public/                    # assets estáticos
├─ angular.json               # builder @angular/build:application, budgets, fileReplacements
├─ tsconfig*.json             # config TS (compila en modo estricto por defecto de TS 6; ver §11)
├─ package.json               # scripts npm (start/build/test/watch)
├─ .prettierrc (100 cols, comillas simples) + .editorconfig
├─ .agents/skills/frontend-design/  # skill de diseño (skills-lock.json)
├─ AGENTS.md                  # este mismo documento (reglas del proyecto)
└─ HISTORIAL.md               # histórico antiguo (referencia)
```

---

## 3. Stack tecnológico (versiones reales del entorno)

### 3.1 Backend (`retro-api`)

| Pieza | Versión / detalle |
|---|---|
| Python | 3.12 en contenedor (`python:3.12-slim`); el host tiene 3.14 (no usar para el proyecto) |
| Django | 6.0.6 |
| Django REST Framework | 3.17.1 |
| SimpleJWT | 5.5.1 (access 60 min, refresh 7 días) |
| drf-spectacular | 0.29.0 (OpenAPI + Swagger + Redoc) |
| django-cors-headers | 4.9.0 |
| django-environ | 0.13.0 (lectura y tipado de `.env`) |
| PostgreSQL | 16 (contenedor `postgres:16`), driver `psycopg2-binary` 2.9.12 |
| Imágenes | Pillow ≥ 10 + `pillow-heif` (HEIC → WebP, quality 80) |
| Docker | Docker 29.6.2 + Compose v5.3.1 |

### 3.2 Frontend (`retro-app`)

| Pieza | Versión / detalle |
|---|---|
| Angular | 22.0.4 (standalone components, `@if`/`@for`, signals, `input()`/`output()`) |
| TypeScript | 6.0.3 |
| RxJS | ~7.8 |
| Estilos | SCSS propio (arquitectura de componentes). **Prohibido Tailwind/Bootstrap** salvo petición expresa |
| Testing | Vitest 4 (+ jsdom) |
| Formato | Prettier 3 (100 cols, comillas simples, parser `angular` en HTML) |
| Gestor de paquetes | npm 10.9.8 (`packageManager` en `package.json`) |

---

## 4. Entorno de desarrollo y comandos

Todos los comandos se ejecutan **desde la carpeta del repo correspondiente**.

### 4.1 Arranque rápido (recomendado)

Desde la carpeta que contiene los dos repos (el espacio de trabajo):

```bash
./start.sh   # levanta la API en Docker (http://localhost:8000) y luego `ng serve --open`
./stop.sh    # docker compose down (el frontend se para con Ctrl+C)
```

### 4.2 Backend

```bash
cd retro-api
docker compose up -d --build                  # db + api
docker compose logs -f api                    # logs en vivo
docker compose exec api python manage.py migrate
docker compose exec api python manage.py makemigrations
docker compose exec api python manage.py createsuperuser
docker compose exec api python manage.py shell
docker compose exec api python verify.py      # conteo de registros (si existe)
docker compose down                           # parar
```

Notas reales del repo: el contenedor se llama `retro_api`, la BD `retro_db`, el puerto de la API
`8000` y el de PostgreSQL en el host `5435`. El servicio `api` monta el código como volumen
(`.:/app`), por lo que los cambios en Python se recargan solos con el `runserver`.

### 4.3 Frontend

```bash
cd retro-app
npm start                 # ng serve → http://localhost:4200
npm run build             # build de producción (budgets + outputHashing)
npm test                  # Vitest
npx prettier --write "src/**/*.{ts,html,scss}"
```

**Aviso comprobado en la práctica:** `ng serve` **no detecta archivos nuevos** (componentes,
servicios, enums, interfaces). Si una tarea crea archivos, hay que **reiniciar el frontend** para
que aparezcan; si solo se modifican archivos existentes, la recarga es automática. El backend sí
recarga solo (el contenedor monta el código como volumen), aunque si se toca `settings.py` conviene
`docker compose restart api`.

### 4.4 URLs locales

| Qué | URL |
|---|---|
| API REST | http://localhost:8000/api/ |
| Login JWT | http://localhost:8000/api/api/token/ |
| Refresh JWT | http://localhost:8000/api/api/token/refresh/ |
| Swagger | http://localhost:8000/api/docs/ |
| Redoc | http://localhost:8000/api/redocs/ |
| Esquema OpenAPI | http://localhost:8000/api/schema/ |
| Admin Django | http://localhost:8000/admin/ |
| SPA Angular | http://localhost:4200/ |

---

## 5. Arquitectura funcional

### 5.1 Dominio

- `ItemBase` (**abstracto**, `inventory/models/Base.py:6`) define lo común: `name`, `model`,
  `acquisition_date`, `price` (precio del artículo), `total_price` (lo pagado con envío y gastos;
  si se deja vacío, se copia `price`), `purchase_url` (enlace del anuncio donde se compró, opcional),
  `status`, `store`, `protective`, `description`, `region`,
  `platform`, `missing_components` (M2M), `complete`, `created_at`, `updated_at` e
  `images` (`GenericRelation` a `ItemImage`).
- Hijos concretos: `Console`, `Game` (ambos con `edition`) y `Accessory`.
- `MissingComponent`: catálogo de piezas que faltan (nombre único).
- `ItemImage` (`inventory/models/Image.py:31`): imagen polimórfica vía
  `ContentType` + `object_id` + `GenericForeignKey`; al guardar convierte a **WebP**
  (calidad 80) con Pillow/pillow-heif y renombra a `.webp`; las rutas se organizan
  como `media/<modelo>s/<slug-nombre>-<id>/<archivo>`; dos signals borran el archivo físico
  al eliminarlo (`post_delete`) o al reemplazarlo (`pre_save`).
- Choices y etiquetas: estado (`SEALED/MINT/GOOD/FAIR`), plataforma (~33 plataformas),
  tienda (13 tiendas), protección (`Sin funda/Bolsa plástica/Funda PET`).
- Usuario: `User(AbstractUser)` con login por **email** (`USERNAME_FIELD = 'email'`).

### 5.2 Contrato de API (autoritativo — **no inventar rutas**)

Base: `http://localhost:8000/api/` (en el frontend sale de `environment.apiUrl` + `/api`).

| Recurso | Rutas | Métodos |
|---|---|---|
| Consolas | `/api/consoles/`, `/api/consoles/{id}/` | GET, POST, PUT, PATCH, DELETE |
| Juegos | `/api/games/`, `/api/games/{id}/` | GET, POST, PUT, PATCH, DELETE |
| Accesorios | `/api/accessories/`, `/api/accessories/{id}/` | GET, POST, PUT, PATCH, DELETE |
| Imágenes | `/api/images/`, `/api/images/{id}/` | GET, POST (multipart), DELETE |
| Componentes faltantes | `/api/components/`, `/api/components/{id}/` | GET, POST, PUT, PATCH, DELETE |
| Auth | `/api/api/token/`, `/api/api/token/refresh/` | POST |

- **Búsqueda**: `?search=` (campos `name`, `model`, `platform`, `region`; en componentes `name`).
- **Ordenación**: `?ordering=name` / `?ordering=-total_price` (permitidos: `name`, `platform`,
  `status`, `created_at`, `price`, `total_price`).
- **Precio**: `price` es el precio del artículo y `total_price` lo pagado con gastos. Si no se envía
  el total, el backend copia `price`; si el total es **menor** que el precio del artículo, la API
  responde 400 con `{"total_price": ["El total no puede ser menor que el precio del artículo."]}`.
- **Enlace de compra**: `purchase_url` es opcional y **solo admite `http` y `https`** (máximo 500
  caracteres). Cualquier otro esquema (`javascript:`, `data:`, `file:`) responde 400. El frontend lo
  abre en pestaña nueva **siempre** con `rel="noopener noreferrer"`.
- **Escritura de M2M**: se envía `missing_component_ids: [1, 2]` (write-only); la lectura devuelve
  `missing_components` (objetos) e `images` (URLs). El serializer expone además
  `status_display` y `platform_display`.
- **Subida de imagen** (`POST /api/images/`, `multipart/form-data`): campos `image`,
  `content_type_model` y `object_id`. Desde E5 (29/09/2026) **`content_type_model` es una lista
  cerrada** (`console` | `game` | `accessory`) y el artículo indicado por `object_id` **tiene que
  existir**; si no, la API responde **400** con el motivo y **no escribe nada en el disco**.
  El objeto destino es obligatorio (`object_id` debe ser ≥ 1).
- **Auth**: access token 60 min, refresh 7 días. Cabecera `Authorization: Bearer <access>`.
  El login se hace con **`email` + `password`** (`SIMPLE_JWT['USERNAME_FIELD'] = 'email'` en
  `core/settings.py`), **no** con `username`. Ojo: la ruta sigue siendo `/api/api/token/`
  (el `api` duplicado es intencionado y está pendiente de normalizar).
- **Permisos**: **toda** la API exige token (`Authorization: Bearer <access>`) desde la tarea E4
  (29/09/2026). Sin token, cualquier recurso responde **401**. Lo único público es
  `/api/api/token/` y `/api/api/token/refresh/` (y `/api/docs/`, `/api/schema/`, que son
  documentación). El defecto global está en `DEFAULT_PERMISSION_CLASSES` (`core/settings.py`):
  **una vista nueva nace protegida**; abrirla exige `permission_classes = [AllowAny]` justificado.
- **Paginación**: hoy **no hay** paginación de DRF configurada → los `GET` de lista devuelven
  un array completo (el frontend pagina en cliente). Ver §11.
- **Errores**: DRF devuelve `{"campo": ["mensaje"]}` con el código HTTP correspondiente
  (400 validación, 401 sin token o token caducado, 403 sin permiso, 404 inexistente,
  500 error interno). El frontend consume esa forma **tal cual**: no se inventan formatos nuevos.

---

### 5.3 Principios de diseño (aplican a todo lo nuevo)

Estos principios son los que hacen que el proyecto se comporte "como en un entorno real". Cuando
haya que elegir entre la solución rápida y la profesional, se elige la profesional y se justifica
el coste en el plan.

1. **Consistencia sobre preferencia personal**: se sigue el patrón que ya existe en el repo. Si un
   patrón se repite en `consoles`, `games` y `accessories`, la solución nueva debe parecerse a
   ellos (o generalizarlos, si toca), nunca inventar un estilo propio.
2. **Simplicidad deliberada**: nada de abstracciones, capas ni ficheros "por si acaso". Si una
   pieza no tiene un uso claro hoy, no se crea.
3. **Una responsabilidad por pieza**: un serializer valida y transforma, una vista orquesta, un
   servicio llama a la API, un componente pinta. Si una pieza hace dos cosas, se parte.
4. **Contrato primero**: antes de tocar código, saber exactamente qué campos entran y salen.
   Ningún cambio rompe el contrato existente (ver §5.4).
5. **Fallar rápido y claro**: configuración obligatoria que revienta al arrancar si falta,
   validación que devuelve 400 con el motivo, errores de UI con mensaje útil. Nada de fallos
   silenciosos.
6. **Trazable**: cada cambio se puede explicar (qué, por qué, dónde y cómo se verifica) y queda
   documentado en el historial. Si no se puede explicar, no está terminado.
7. **Reversible**: toda migración y todo cambio de datos se piensa también "hacia atrás"
   (cómo volver al estado anterior).

### 5.4 Evolución del contrato de API (sin romper el frontend)

- **Añadir** campos nuevos: permitido, siempre **opcionales o con valor por defecto** en el
  serializer, y actualizando a la vez la interfaz del frontend.
- **Quitar o renombrar** campos existentes: **prohibido** sin plan aprobado y sin actualizar el
  frontend en la misma tarea (los dos repos están acoplados por el contrato).
- **Cambiar el tipo** de un campo: se trata como ruptura; requiere plan propio.
- Los campos nuevos se documentan en §5.2 de este archivo al cerrar la tarea confirmada.
- Versionar la API (`/api/v1/`) queda como decisión pendiente del humano (ver §13.1): hoy el
  contrato se mantiene compatible a mano.

---

## 6. Convenciones de código (obligatorias)

### 6.1 Idioma

- Comentarios, docstrings, textos de UI y documentación: **español**.
- Código (nombres de clases, funciones, variables, campos, claves JSON de la API): **inglés**.
- Nunca renombrar campos del contrato (`name`, `platform_display`, `missing_component_ids`…):
  hay dos repos acoplados por ese contrato.

### 6.2 Backend (Python / Django / DRF)

- Estilo: PEP 8, `snake_case` para funciones/variables, `PascalCase` para clases.
- **Un modelo por archivo** en `inventory/models/` con el nombre del modelo en `PascalCase.py`.
  Un modelo nuevo del dominio hereda de `ItemBase` para no duplicar campos.
- **Un serializer por modelo** en `inventory/api/serializers/`; los campos derivados van como
  `read_only` (`*_display`), y la entrada de relaciones se hace por IDs (`*_ids`, write-only).
- **Un ViewSet por recurso** en `inventory/api/views/` con nombre `view_<recurso>.py`, registrado
  en `inventory/api/router.py` con `basename` explícito.
- Consultas siempre optimizadas (ver §7.1) y permisos declarados explícitamente (ver §8.1).
- Validaciones de negocio en el serializer (`validate_*` / `validate`), nunca en la vista.
- **Admin**: si un `ModelAdmin` declara `fields`/`fieldsets`, cada nombre debe existir en **su**
  modelo. Un nombre que no exista **no lo detecta `manage.py check`**: Django lanza
  `FieldError: Unknown field(s) (…) specified for …` al **abrir** esa página (un 500 en la cara del
  usuario). Lo vigila `inventory/tests/test_admin_inventario.py`; al tocar el admin, ejecutarlo.
  Pasó en D2: se copió el bloque de `Console` (que tiene `edition`) a `Accessory`, que no lo tiene.
- Migraciones: **nunca** editar una migración ya aplicada; crear una nueva y describirla.
- Nada de lógica pesada en `save()` del modelo salvo el procesado de archivos ya existente.
- `settings.py` lee todo del entorno con `django-environ` (fail-fast). No hardcodear secretos.

### 6.3 Frontend (Angular)

- Estilo: `kebab-case` para archivos, `camelCase` para miembros, `PascalCase` para clases.
- Componentes **standalone** con `imports: []`; nunca `NgModule` nuevos salvo petición expresa.
- Estado con **signals** (`signal`, `computed`, `input()`, `output()`); RxJS solo para HTTP,
  eventos y cancelación.
- Estructura de feature: `<feature>/<feature>.service.ts`, `<feature>.routes.ts` y
  `list/`, `detail/`, `form/` con su `.ts` + `.html` + `.scss` (el `styleUrl` siempre separado).
- Servicios: `inject()` en lugar de constructor, `providedIn: 'root'` y **un endpoint por
  servicio**; toda llamada HTTP pasa por `core/api.service.ts` (nunca `HttpClient` directo en
  componentes) y la URL base sale de `environment`.
- Interfaces en `src/app/models/*.interface.ts`, enums en `*.enum.ts` y **exportadas en el barrel**
  `src/app/models/index.ts`; los features importan del barrel.
- **Prohibido `any`** (los genéricos de `ApiService` usan `unknown`). Todo dato de la API se tipa.
- Importar tipos con `import type { … }` (el proyecto ya usa `isolatedModules`).
- Formularios: `ReactiveFormsModule` con `FormBuilder` y `Validators`.
- Plantillas: flujo de control nuevo (`@if`, `@for`, `@switch`), nunca `*ngIf`/`*ngFor` en código
  nuevo; `@for` **con `track`** obligatorio.
- Estilos: variables/SCSS por componente, sin librerías de UI externas.
- Textos de UI y comentarios en español; identificadores en inglés.

### 6.4 Testing (obligatorio en código nuevo)

**Regla**: ninguna tarea se marca como terminada si su lógica nueva no tiene al menos un test que
la cubra, o si no se ha justificado por qué no aplica. "Funciona cuando lo pruebo a mano" no es
suficiente para lógica de negocio, validaciones ni permisos.

Backend (`retro-api`):
- **Runner actual: el de Django** (`python manage.py test`). Los tests viven en
  `inventory/tests/` (paquete con `__init__.py`) y `user/tests/`, un archivo por área:
  `test_models.py`, `test_serializers.py`, `test_views.py`, `test_images.py`, y
  `test_<tarea>.py` para los tests que entran con una tarea concreta (ej.: `test_a1_login.py`).
- **Pendiente de decidir**: adoptar además `pytest` + `pytest-django` (y `factory_boy` para datos
  de prueba). Mientras no se decida, no se añaden esas dependencias y se usa el runner de Django.
- Cada test declara el caso que cubre: camino feliz **y** errores (datos inválidos, sin
  autenticación, sin permiso, objeto inexistente).
- Obligatorio test explícito de:
  - **permisos** (401 sin token, 403 sin permiso) en cada recurso tocado;
  - **validaciones del serializer** (cada `validate_*` nuevo);
  - **N+1**: `assertNumQueries` en los listados que serializan relaciones;
  - **subida y borrado de imágenes** (creación del `.webp` y limpieza del archivo físico).
- Comando: `docker compose exec api python manage.py test` (usa una base de datos temporal, nunca
  la de desarrollo). Para una sola tarea:
  `docker compose exec api python manage.py test inventory.tests.test_a1_login`.
- **Ojo con la estructura de tests**: Django falla con `ImportError: 'tests' module incorrectly
  imported` si conviven `<app>/tests.py` (el archivo vacío que trae Django) y `<app>/tests/`
  (el paquete). Es un choque que **ya ha pasado tres veces** (en `inventory` al crear sus tests, y
  en `user` en D2 y E6): **los tests van en el paquete** `<app>/tests/` con su `__init__.py`, así
  que al crear tests en una app nueva hay que **borrar su `tests.py`**. Si la app no va a tener
  tests todavía, no se crea la carpeta.

Frontend (`retro-app`):
- Framework: **Vitest** (ya configurado con jsdom) + `HttpTestingController` para HTTP.
- Cada componente/servicio nuevo lleva su `.spec.ts` al lado del archivo
  (`list.component.spec.ts`).
- Cubrir: lógica de los `computed`, transformación de datos, manejo de error de la API y los
  **cuatro estados de UI** (carga, vacío, error, datos) del §12.4.
- Los componentes se prueban con `TestBed`; nunca se llama a un servicio real (mock o
  `HttpTestingController`).
- Comando: `npm test`.

Reglas comunes:
- Los tests son **deterministas**: sin depender de la fecha actual, la red, servicios externos ni
  del orden de ejecución.
- Nada de tests que solo comprueben que "no explota": cada test verifica un comportamiento.
- Los datos de prueba se crean **dentro del test** y se limpian (aislamiento entre tests).

### 6.5 Higiene del código generado

- **Prohibido** dejar `console.log`/`print()` de depuración, código comentado, bloques muertos,
  `TODO`/`FIXME` sin dueño y fecha, o imports sin usar.
- **Prohibido** dejar código a medias "para la siguiente tarea": o entra completo en esta tarea, o
  no entra (se anota en el plan como tarea futura).
- Nada de copiar y pegar entre `consoles`, `games` y `accessories`: si el cambio aplica a los
  tres, se hace en los tres de forma consistente y se valora generalizarlo (§7.2).
- Las interfaces del frontend reflejan **exactamente** los campos que devuelve el serializer
  (mismos nombres, mismo tipo, misma nulabilidad).
- Los mensajes visibles al usuario van en español y explican qué hacer; los internos (logs) pueden
  ser técnicos.
- Antes de cerrar la tarea: cero errores de compilación, cero warnings nuevos relevantes y
  `npx prettier --check` en verde para lo tocado.

---

## 7. Eficiencia (rendimiento obligatorio)

### 7.1 Backend

- **Cero N+1**: todo ViewSet declara `select_related`/`prefetch_related` en su `queryset`
  (hoy ya se hace con `missing_components` e `images`; añadir `content_type` cuando se serialicen
  imágenes). Verificar con `django-debug-toolbar` o `assertNumQueries` en tests.
- Usar `only()`/`defer()` en listados si se traen columnas que no se serializan.
- Escrituras masivas con `bulk_create`/`bulk_update`; M2M con `set()` en lugar de bucles.
- Índices en BD solo cuando haya consultas reales que lo justifiquen (`db_index`, `Meta.indexes`),
  justificando el cambio en el plan de la tarea.
- Trabajo pesado (conversión de imágenes, importaciones) fuera del ciclo petición/respuesta.
- Respuestas de lista con paginación cuando el dataset crezca (ver §11).

### 7.2 Frontend

- `changeDetection: ChangeDetectionStrategy.OnPush` en componentes nuevos y al tocar los existentes.
- Nada de llamadas a funciones costosas desde la plantilla: usar `computed()`.
- Desuscripción obligatoria: `takeUntilDestroyed()`/`takeUntil(destroy$)` o pipe `async`. Sin fugas.
- Búsquedas e inputs: `debounceTime` + `distinctUntilChanged` + `switchMap` (patrón ya usado en
  las listas). Nada de `subscribe` anidados.
- Bundle: respetar los budgets de `angular.json` (inicial 500 kB warning / 1 MB error; estilos por
  componente 6 kB / 12 kB) y mantener **lazy loading** de features y componentes.
- Imágenes: usar las URLs que ya vienen optimizadas a WebP desde el backend + `loading="lazy"`
  donde aplique.
- Reutilizar `shared/` y `core/` antes de crear código nuevo; cero duplicación entre
  `consoles`, `games` y `accessories` (si el patrón se repite 3 veces, se generaliza).
- **Buscadores: dejar el `<input>` sin enlazar al componente.** Se lee su valor con
  `(input)="onSearch($any($event.target).value)"` y, si hay que limpiarlo desde código, se usa una
  referencia de plantilla (`#searchInput`). Enlazarlo a un valor que dependa de una respuesta del
  backend hace que el texto se pierda mientras se escribe (pasó en el intento descartado de C1).
- **Estado de interfaz en memoria antes que en la URL.** Para filtros de lista (búsqueda,
  plataforma, orden), guardar el estado en un servicio (`core/`) y recuperarlo al volver. La URL se
  reserva para lo que de verdad deba compartirse o sobrevivir a un recargado. El intento de mover
  los filtros a la URL (29/09/2026) se descartó: rompió la carga inicial y multiplicó las peticiones
  por palabra. Ver `retro-app/docs/history/2026-09-mejoras-inventario.md`.
- **Cuidado con la reactividad de más.** Si dos flujos distintos (cambios de filtro y cambios de la
  URL) pueden provocar la misma recarga, hay que **agrupar las ráfagas en una sola petición**: el
  retardo (`debounceTime`) va **después** de juntar los flujos, nunca antes. Y si se usa
  `combineLatest`, comprobar que **todos** los flujos emiten al arrancar, o la primera carga no
  ocurrirá (fue el otro fallo del intento descartado).

### 7.3 Transacciones y consistencia de datos (backend)

- **Todo** cambio que toque más de una tabla o más de un registro va envuelto en
  `transaction.atomic()`: crear/editar un ítem con sus `missing_components` y sus imágenes, altas
  masivas, importaciones. Si falla un paso, no queda nada a medias.
- Las vistas que reciben lotes (`many=True`) se implementan con `bulk_create`/`bulk_update` dentro
  de una transacción, nunca con bucles de `save()`.
- **Ojo con las señales de archivos**: `post_delete`/`pre_save` de `ItemImage` borran del disco
  fuera del control transaccional. Regla: **la fila primero, el archivo después**, y el borrado
  físico siempre tolerante a fallos (si el archivo ya no está, la petición no se rompe).
- **Concurrencia**: cuando una tarea permita modificar el mismo registro desde dos peticiones a la
  vez (contadores, `complete`, stock), usar `select_for_update()` dentro de la transacción y
  explicarlo en el plan de la tarea.
- Las migraciones con datos se escriben de forma **idempotente** y con su operación inversa cuando
  sea posible (§12.3).

---

## 8. Seguridad (obligatorio en todo cambio)

### 8.1 Backend

- **Permisos explícitos** en cada vista: `permission_classes = [IsAuthenticated]` por defecto y
  `permission_classes = [AllowAny]` solo donde se justifique (login, registro). Regla de oro:
  **denegar por defecto**.
- Validación **siempre** en el serializer: tipos, longitudes, límites, pertenencia y existencia de
  las FK referenciadas (p. ej. que `object_id` apunte a un objeto real del `content_type`).
- Subida de archivos: validar tipo real (MIME/contenido, no la extensión), tamaño máximo y
  extensión; nunca confiar en el nombre original (la ruta se construye ya con `slugify`).
- Consultas siempre por ORM parametrizado. Prohibido SQL crudo con interpolación y prohibido
  `eval`/`exec`/`pickle` con datos de entrada.
- Nunca exponer `SECRET_KEY`, `DEBUG`, credenciales, tokens ni rutas internas en respuestas.
- `DEBUG=False` y `SECRET_KEY` rotada antes de producción; `ALLOWED_HOSTS` restrictivo.
- CORS con lista blanca exacta por entorno; nada de `CORS_ALLOW_ALL_ORIGINS`.
- Autenticación/autorización comprobada en el servidor siempre: el guard del frontend es UX,
  no seguridad.
- Errores: mensajes claros para el usuario, sin filtrar trazas ni detalles internos.

### 8.2 Frontend

- Sin `any`; sin `innerHTML` con datos de la API (riesgo de XSS). Si hace falta HTML dinámico,
  sanitizar y justificarlo.
- Los tokens JWT viven en `localStorage` (estado actual) → todo dato pintado se trata como
  no confiable. Ver §11 para la alternativa con cookies `HttpOnly` (requiere cambio en backend).
- No confiar en el cliente para permisos ni validaciones críticas.
- Sin secretos, claves ni URLs privadas en el bundle (`environment.*` es público por definición).
- Actualizar dependencias solo con justificación y verificando `npm audit` / `pip-audit`.

### 8.3 Cabeceras de seguridad y limitación de peticiones (backend)

- Django ya trae las defensas base activadas en `MIDDLEWARE` (`SecurityMiddleware`,
  `CsrfViewMiddleware`, `XFrameOptionsMiddleware`). En producción, además, con `DEBUG=False`:
  `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`
  (empezando bajo y subiendo), `SECURE_CONTENT_TYPE_NOSNIFF` y `X_FRAME_OPTIONS`. Se activan por
  entorno, nunca en duro (§12.1).
- El admin de Django (`/admin/`) no se expone públicamente sin necesidad.
- `ALLOWED_HOSTS` y `CORS_ALLOWED_ORIGINS` son listas **exactas** por entorno: nada de comodines.
- **Throttling de DRF: ya está puesto** (tarea E6, 30/09/2026). Los límites viven en
  `DEFAULT_THROTTLE_RATES` (`core/settings.py`) y cada vista los activa con `throttle_scope`:
  `login` y `refresh` a **10/min**, `subida` de imágenes a **20/hora**. Los contadores son
  independientes entre sí. Cualquier endpoint sensible nuevo debe llevar su propio ámbito.
  - Para eximir al dueño (`is_staff`) se usa `user/api/throttles.py` → `ThrottleConExencionStaff`.
    **Ojo**: la exención solo actúa donde la petición ya va autenticada. En el **login no funciona**
    (quien pide un token todavía es anónimo, así que el límite se cuenta por IP); está documentado
    en el código y fijado con un test, no es un fallo.
  - Los límites **no se pueden cambiar con `override_settings` en los tests**: DRF los lee una sola
    vez al cargar su módulo (`SimpleRateThrottle.THROTTLE_RATES` es un atributo de clase). Los
    tests de throttling usan los límites reales y limpian la caché en `setUp`, porque los
    contadores no se borran solos entre tests.
- Los errores de autenticación no revelan si el fallo es el email o la contraseña.
- Ninguna respuesta incluye versión del servidor, trazas ni rutas internas.

### 8.4 Datos sensibles: logs, respuestas y ficheros (backend)

- **Nunca** se registran en logs: contraseñas, tokens JWT (ni completos ni parciales),
  `SECRET_KEY`, credenciales de BD, cabeceras `Authorization` ni datos personales innecesarios.
- Los serializers de usuario marcan `password` como `write_only` **siempre** y se hashean con
  `create_user`/`set_password`; jamás se devuelve un hash por la API.
- Al registrar autenticación se anota **email + resultado + IP**, nunca la contraseña.
- Los ficheros subidos no se sirven con rutas adivinables ni se confía en el nombre original.
- Un endpoint devuelve **solo** los campos del contrato: nada de serializar el modelo entero ni
  `__dict__` "por comodidad".

### 8.5 Checklist de seguridad por tarea (backend)

- [ ] `permission_classes` explícitos y correctos en cada vista tocada.
- [ ] Toda entrada validada en el serializer (incluida la existencia de las FK referenciadas).
- [ ] Ninguna consulta construida concatenando strings.
- [ ] Ningún dato sensible en respuesta ni en logs.
- [ ] Si hay subida de ficheros: tipo real, tamaño máximo y extensión comprobados.
- [ ] Si el endpoint es sensible (login, subida): throttling definido.
- [ ] Secretos y flags de producción leídos del entorno, nunca en duro.

---

## 9. Protocolo de trabajo (NO negociable)

### 9.1 Reglas de oro

1. **Nunca tocar GitHub ni Git.** El humano gestiona `commit`, `push`, `pull`, `branch`, `merge`,
   `rebase` y los PRs. El agente **no** ejecuta comandos de Git, no crea ramas, no hace `stage` y
   no escribe mensajes de commit. Solo modifica archivos en el working tree.
2. **Avisar siempre antes de cambiar código.** En cada funcionalidad: primero el plan, luego
   implementar. Nunca cambios silenciosos ni "de paso" (refactors, renombrados, formateos masivos)
   que no estén en el plan aprobado.
3. **Una tarea a la vez.** No se empieza la siguiente hasta que la anterior esté confirmada.
4. **Verificación antes de dar nada por hecho**: compilar/ejecutar lo que se pueda y decir
   exactamente qué comandos se han usado.
5. **Si hay dudas, preguntar** antes de asumir (endpoint, campo, comportamiento, ubicación de un
   archivo). Mejor una pregunta que un cambio equivocado.
6. **Respetar la estructura** de carpetas de §2 y las convenciones de §6. Cualquier archivo nuevo
   va donde le corresponde por patrón, no donde sea más rápido.

### 9.2 Ciclo obligatorio de cada tarea (con puerta de confirmación)

```
1. PLAN     → el humano dicta el listado de tareas; se anota en docs/PLAN.md
              (objetivo, alcance, tareas numeradas, criterio de aceptación, riesgos).
2. AVISO    → antes de escribir código: qué se va a tocar (archivos) y cómo. OK del humano.
3. IMPLEMENTAR una única tarea del plan (la marcada como en curso).
4. VERIFICAR  → ejecutar build/tests/comprobación manual y recoger el resultado real.
5. PREGUNTAR  → explicar qué tiene que hacer el humano para comprobarlo y terminar con
                literalmente: "¿Todo bien?"
                ↓
        ⛔ AQUÍ SE PARA. No se documenta, no se completa la tarea, no se avanza,
           no se toca nada más (ni "arreglos pequeños") hasta que el humano confirme.
                ↓
6. Si el humano dice que NO (o pide cambios) → corregir y volver al paso 4.
   Si dice que SÍ (bien / ok / correcto):
      a. Escribir el documento de la tarea (plantilla de §10) en la carpeta de historial.
      b. Marcar la tarea como completada en docs/PLAN.md (con fecha y enlace al documento).
      c. Pasar a la siguiente tarea del plan (volviendo al paso 2).
```

Regla dura: **sin la confirmación explícita del humano, la tarea permanece "en curso"** y no se
considera terminada, aunque el código ya funcione.

### 9.3 Qué NO hace el agente

- No hace operaciones de Git/GitHub (ver §9.1).
- No cambia código sin avisar antes.
- No completa una tarea sin confirmación.
- No añade librerías nuevas ni cambia versiones por iniciativa propia.
- No modifica `backup.sql`, `restore_data.py`, migraciones ya aplicadas ni `.env`.
- No borra ni renombra archivos existentes sin autorización explícita.

### 9.4 Convención de ramas y commits (la aplica el humano)

El agente **no ejecuta** ningún comando de Git (§9.1.1). Esta convención existe para que las
propuestas del agente encajen con el trabajo del humano y para que el historial sea legible.

- **Nunca se trabaja en `main`** para una funcionalidad nueva: cada funcionalidad va en su rama,
  creada desde `main` actualizado. Ramas existentes de despliegue: `despliegue-render` (API) y
  `despliegue-vercel` (frontend).
- **Nombres de rama** (una rama = una tarea o un listado pequeño y coherente):
  - `feat/<slug>` — funcionalidad nueva.
  - `fix/<slug>` — corrección de un fallo.
  - `refactor/<slug>` — cambio interno sin cambio de comportamiento.
  - `docs/<slug>` — solo documentación.
  - `chore/<slug>` — dependencias, configuración, mantenimiento.
- **Commits (Conventional Commits)**:
  `<tipo>(<ámbito>): <descripción en imperativo y en español>`
  - Tipos: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`.
  - Ámbitos: `api`, `inventory`, `user`, `app`, `core`, `ui`.
  - Ejemplos: `feat(api): permisos explícitos en los viewsets de inventario` ·
    `fix(app): refrescar el token una sola vez con varias peticiones 401`.
- **Un commit = un cambio coherente y explicable**. Nada de commits "varios cambios" mezclando
  backend y frontend sin relación.
- **Cada tarea del plan = una rama**, y su PR se abre tras la confirmación del humano.
- El agente, cuando corresponda, **propone** el nombre de rama y el mensaje de commit en la
  documentación de la tarea; el humano decide, ejecuta y sube.
- El documento de historial de la tarea (§10.2) anota la rama realmente usada.
- Consecuencia práctica: la rama **debe** indicarse antes de tocar código, porque el agente trabaja
  sobre el working tree que el humano tenga activo; si hay dudas de en qué rama está, se pregunta.
- Existe una decisión pendiente sobre artefactos versionados (`retro-app/dist/`, `retro-api/media/`,
  `skills-lock.json`): ver §13.2.

---

## 10. Documentación de tareas

### 10.1 Dónde vive

| Documento | Ubicación | Contenido |
|---|---|---|
| Plan del listado de tareas | `docs/PLAN.md` (raíz del workspace; **pendiente de mover a `retro-api/docs/PLAN.md`** para que se versione en Git) | objetivo, tareas numeradas y su estado, criterio de aceptación |
| Historial de tareas del backend | `retro-api/docs/history/` | **un `.md` por listado de tareas** con las tareas completadas y confirmadas del backend |
| Historial de tareas del frontend | `retro-app/docs/history/` | igual, cuando el listado afecte al frontend |

Reglas de nombrado:

- Un documento de historial **por cada listado de tareas** que entregue el humano (no uno por
  tarea suelta ni un único archivo global que crezca sin control).
- Nombre sugerido: `AAAA-MM-DD-<slug-del-listado>.md`
  (ej.: `2026-09-28-mejoras-seguridad-api.md`).
- Solo se escribe historial de tareas **completadas y confirmadas** por el humano.
- Las tareas de backend se documentan en `retro-api/docs/history/`; las de frontend en
  `retro-app/docs/history/`; un listado mixto genera **un documento en cada repo** con lo que le
  toca (nunca duplicar contenido entre repos).

### 10.2 Plantilla obligatoria por tarea

Cada tarea dentro del documento de historial debe incluir, **con estos apartados y en este orden**:

```markdown
### N. Nombre de la tarea

- **¿Qué realiza?:** descripción funcional breve y concreta.
- **¿Por qué?:** motivo/necesidad (problema que resuelve).
- **Dónde verlo:**
  - `ruta/al/archivo.ts` (líneas X-Y: qué hay ahí)
  - `ruta/al/otro.html` (líneas X-Y)
- **Cómo verificar:** pasos exactos y verificables (comando a ejecutar y resultado esperado,
  o navegación concreta en la UI: URL, clic, qué debe verse).
- **Tests añadidos:** archivo de test y qué caso cubre (o "no aplica" justificado).
- **Rama de trabajo:** nombre de rama que el humano ha usado para esta tarea (informativo,
  §9.4; el agente no crea ni cambia ramas).
- **Estado:** Completada — confirmada por el humano el AAAA-MM-DD.
```

Requisitos de calidad del documento:

- Las referencias de archivo y líneas deben ser **reales y comprobadas** en el momento de
  escribirlo (no aproximadas ni inventadas).
- "Cómo verificar" debe poder seguirlo otra persona sin contexto previo.
- Si la tarea dejó deuda técnica o algo pendiente, se anota al final de su apartado.

### 10.3 Formato del plan (`docs/PLAN.md`)

```markdown
# PLAN — <nombre del listado>

- **Objetivo:** …
- **Alcance:** backend / frontend / ambos
- **Criterio de aceptación:** …

## Tareas

- [ ] **1. <tarea>** — <una línea de qué se hará> · repo: `retro-api`
- [x] **2. <tarea>** — Completada el AAAA-MM-DD · doc: `retro-api/docs/history/<archivo>.md`
- [ ] **3. <tarea>** — 🚧 EN CURSO (no completar sin confirmación del humano)
```

El plan se actualiza **solo** cuando el humano confirma la tarea.

---

## 11. Estado conocido y deuda técnica (NO arreglar sin autorización)

Lista de hallazgos reales detectados al leer el código. Son **puntos a decidir con el humano**,
no una lista de cambios a ejecutar:

**Contrato / arquitectura**
1. `AuthService` apunta a `${apiUrl}/api/api` y las rutas JWT son `/api/api/token/`
   (doble `api`). Funciona, pero conviene decidir si se normaliza.
2. ✅ **RESUELTO (tarea A1, 29/09/2026)**: el login del frontend envía `{ email, password }` y
   `TokenObtainPairView` esperaba `username`. Arreglado con `'USERNAME_FIELD': 'email'` en
   `SIMPLE_JWT` (`core/settings.py`). Cubierto por `inventory/tests/test_a1_login.py`.
   *(Histórico: el problema era que el email se enviaba a un endpoint que esperaba `username`.)*
3. `inventory/api/serializers/item_base.py` (`ItemBaseSerializer`) parece no usarse: los
   serializers de cada recurso están duplicados entre sí.
4. `restore_data.py` y `verify.py` ejecutan consultas al importar el módulo (sin `main()` ni
   guardas): conviene envolverlos antes de reutilizarlos.

**Seguridad**
5. ✅ **RESUELTO (tarea E4, 29/09/2026)**: los ViewSets no declaraban `permission_classes` y DRF,
   al no tener `DEFAULT_PERMISSION_CLASSES`, **permitía todo**: sin token se leía, se creaba, se
   editaba y se **borraba** el inventario. Ahora `DEFAULT_PERMISSION_CLASSES` es
   `IsAuthenticated` (`core/settings.py`) y cada ViewSet lo declara explícitamente. Cubierto por
   `inventory/tests/test_e4_permisos.py` (10 tests).
6. ✅ **RESUELTO en parte (tarea E4, 29/09/2026)**: `RegistroView` pasó de `permission_classes = []`
   a `AllowAny` (explícito). **Pero además se descubrió que esa vista no tiene ruta**: `POST
   /api/register/` devuelve 404, es **código muerto**. Decidir si se conecta o se elimina sigue
   pendiente (ver §13.7).
7. `.env` con `DJANGO_DEBUG=True`, `ALLOWED_HOSTS` local y una `SECRET_KEY` `django-insecure-*`:
   hay que rotarla y separar configuración de desarrollo/producción antes de desplegar.
   El `.env` está en `.gitignore` (bien) y no debe versionarse nunca.
8. ✅ **RESUELTO (tarea E5, 29/09/2026)**: la subida de imágenes aceptaba cualquier `object_id`
   (creaba carpetas fantasma `unknown-<id>`), un `content_type_model` inventado daba **500 con la
   traza** y se podían colgar fotos de modelos que no deben llevarlas. Ahora el destino está en
   lista cerrada (`console`/`game`/`accessory`) y el artículo debe existir; si no, **400**. Cubierto
   por `inventory/tests/test_e5_imagenes.py` (10 tests).
9. `Dockerfile` no define `USER` no-root ni `CMD` por defecto (el comando lo pone
   `docker-compose.yml` como `runserver`, solo para desarrollo).
10. Los signals de borrado de imágenes usan `os.remove` apoyándose en `instance.image.path`
    (depende del backend de almacenamiento local); revisar si algún día se usa almacenamiento
    remoto.
11. `CORS_ALLOW_CREDENTIALS = True` es innecesario mientras el JWT viaje en cabeceras.

**Rendimiento**
12. DRF no tiene paginación configurada y el frontend pagina en cliente (carga la lista
    completa en memoria). Es aceptable con pocos cientos de registros; a partir de ahí hay que
    decidir paginación en servidor.
13. El interceptor del frontend no deduplica refresh: varias respuestas 401 simultáneas lanzan
    varios `refresh` y, si el refresh falla, reintenta sin límite.
14. `authGuard` solo comprueba que exista un token en `localStorage`, no su expiración.
15. Guardar JWT en `localStorage` es sensible a XSS; la alternativa robusta (cookie `HttpOnly`)
    exige cambios coordinados en backend (CORS + CSRF) y debe planificarse como tarea propia.

**Higiene**
16. `retro-app/HISTORIAL.md` está obsoleto (Jasmine/Karma, `/api/v1/`, rutas de archivos que ya
    no existen). Se conserva como referencia histórica.
17. `retro-api/README.md` documenta `/api/v1/...` cuando las rutas reales son `/api/...`.
18. Sin trackear en Git (decisión del humano): `retro-api/backup.sql`, `restore_data.py`,
    `verify.py`, y varias migraciones 0006-0012.
19. `tsconfig.json` no declara `strict: true` explícitamente (TS 6 compila estricto por defecto,
    pero la intención conviene dejarla escrita junto a `noUncheckedIndexedAccess`).

---

## 12. Entorno real: despliegue, observabilidad y UI

Esta sección es la que convierte el proyecto en algo que se puede poner delante de usuarios reales
sin sorpresas.

### 12.1 Configuración por entorno (dev / staging / producción)

- Todo lo que cambia entre entornos vive en variables de entorno y en `environment.*.ts`; **nunca**
  en el código.
- Backend (variables que deben existir en cada entorno):
  `DJANGO_SECRET_KEY` (distinta por entorno), `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`,
  `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, y en producción además: orígenes
  CORS permitidos, flags `SECURE_*` y, si aplica, almacenamiento de media.
- Reglas:
  - `DEBUG=False` **siempre** en producción (con `DEBUG=True` Django muestra trazas y consultas).
  - `SECRET_KEY` propia de cada entorno y rotada si alguna vez se ha compartido o subido.
  - `ALLOWED_HOSTS` y CORS: dominios reales, sin comodines.
  - Los secretos se inyectan desde el panel del proveedor (Render u otro), **no** desde el repo.
    El `.env` es solo para desarrollo local y está en `.gitignore`.
  - Nunca se reutiliza la base de datos de desarrollo como producción.
  - `SECURE_HSTS_SECONDS` se activa con un valor bajo y se sube de forma escalonada.
- Frontend: `src/environments/environment.ts` (producción) y `environment.development.ts`
  (desarrollo) solo contienen `apiUrl` y flags públicos (`production`). Nada de secretos: el
  contenido de `environment` acaba en el bundle y es público por definición.

### 12.2 Checklist de despliegue (se recorre entero, en orden)

1. Los tests pasan en local (`pytest` / `npm test`) y el build de producción compila
   (`npm run build`, sin warnings nuevos).
2. Las migraciones nuevas se han probado en local con una copia de datos reales.
3. **Backup de la base de datos** antes de aplicar nada.
4. Aplicar migraciones: `docker compose exec api python manage.py migrate`.
5. Arrancar la API y comprobar: `/api/docs/` responde, `/api/schema/` genera sin errores y los
   logs no muestran excepciones.
6. Probar el flujo crítico contra el entorno real: login, listado, detalle, creación/edición de un
   ítem y subida de una imagen.
7. Desplegar el frontend y verificar que apunta a la API correcta (no a `localhost`).
8. Revisar los logs de error durante los primeros minutos de uso.
9. Si algo falla: revertir la migración concreta si existe su inversa; si no, restaurar el backup.
   Nunca "arreglar a mano" datos en producción sin dejar constancia.

### 12.3 Migraciones seguras (sin romper producción)

- **Nunca** se edita una migración ya aplicada en otro entorno: se crea una nueva encima.
- Cambios incompatibles (renombrar, cambiar tipo, hacer obligatorio un campo) se hacen **en pasos
  separados**: (1) añadir campo opcional → (2) migrar datos → (3) hacerlo obligatorio y eliminar lo
  viejo, en tareas y despliegues distintos.
- Las migraciones con datos usan `RunPython` con función inversa (o `RunPython.noop` justificado y
  documentado) y son **idempotentes**.
- Operaciones que bloquean tabla (índices grandes, cambios de tipo) se planifican sabiendo el
  impacto y se ejecutan en ventana de baja actividad.
- Antes de tocar esquema: **backup** y comprobación de que la migración hacia atrás funciona.
- `makemigrations` se ejecuta en el contenedor, y la migración resultante se revisa a mano antes de
  darla por buena.

### 12.4 Observabilidad (logs)

- Uso del logger de Django (`logging.getLogger(__name__)`), **nunca** `print()`. La configuración
  `LOGGING` va en `settings.py` y cambia por entorno (consola en desarrollo, consola + fichero o
  proveedor en producción).
- Formato mínimo: timestamp, nivel, logger y mensaje. Niveles:
  - `DEBUG` solo en desarrollo.
  - `INFO` para hitos de negocio relevantes (no para cada petición).
  - `WARNING` para situaciones recuperables (fichero que ya no existe al borrar).
  - `ERROR`/`exception` para fallos reales.
- `logger.exception` dentro de bloques `except` para no perder la traza (nunca `logger.error` a
  secas cuando hay excepción).
- **Prohibido** loguear datos sensibles (§8.4).
- Nada de loguear en exceso: si un log no ayuda a diagnosticar, no se escribe.
- Un identificador de petición (request id) facilita seguir un problema cuando haya varias
  peticiones mezcladas: se añade solo si una tarea lo necesita de verdad.

### 12.5 Estados de UI obligatorios (frontend)

Toda vista que consume datos debe contemplar y verse bien en los **cuatro estados**:

1. **Carga**: spinner/skeleton, sin saltos bruscos de layout.
2. **Vacío**: mensaje claro que explique que no hay datos y qué hacer ("Todavía no hay juegos").
3. **Error**: mensaje en español y, cuando tenga sentido, botón de reintentar. Nunca pantalla en
   blanco ni error técnico crudo.
4. **Datos**: contenido normal.

Aplicación concreta: las listas necesitan carga/vacío/error; los detalles, carga/error; los
formularios, enviando/error de validación; las imágenes, placeholder cuando el ítem no tiene
ninguna. Ningún estado puede quedar sin definir.

### 12.6 Accesibilidad y criterio visual (frontend)

- Todo campo de formulario lleva su `<label>` asociado (`for`/`id`); nada de depender del
  placeholder como etiqueta.
- Todo elemento interactivo es alcanzable y usable con teclado, y muestra el foco de forma visible.
- Contraste suficiente de texto sobre fondo, también en la estética retro.
- HTML semántico (`nav`, `main`, `section`, `button` cuando es acción y `a` cuando es navegación);
  `aria-*` solo cuando el HTML nativo no baste.
- Imágenes de producto con `alt` descriptivo y `loading="lazy"` donde aplique.
- El enfoque visual lo marcan `src/styles.scss` y la skill `frontend-design`: no se introducen
  estilos por componente que rompan la coherencia ni librerías de UI externas.

### 12.7 Levantar el proyecto desde cero (onboarding)

```bash
# 1) Backend
cd retro-api
cp .env.example .env      # si no existe .env.example, se pide el contenido (hoy el .env real no se versiona)
nano .env                 # DJANGO_SECRET_KEY propia, credenciales de BD, DEBUG=True
docker compose up -d --build
docker compose exec api python manage.py migrate
docker compose exec api python manage.py createsuperuser
# (opcional) restaurar datos: docker compose exec -T db psql -U <usuario> -d <bd> < backup.sql

# 2) Frontend
cd ../retro-app
npm ci                    # reproducible, requiere package-lock.json versionado
npm start                 # http://localhost:4200
```

Si algo no arranca, estas son las causas típicas en este proyecto:

| Síntoma | Causa habitual | Qué revisar |
|---|---|---|
| La API no arranca | Falta una variable obligatoria en `.env` | Logs del contenedor `retro_api` |
| Error de conexión a BD | `DB_HOST` incorrecto (dentro de Docker es `db`, no `localhost`) o puerto ocupado | `docker compose ps`, logs de `retro_db` |
| 400 "DisallowedHost" | `DJANGO_ALLOWED_HOSTS` sin el host usado | `.env` |
| Error CORS en el navegador | El origen no está en `CORS_ALLOWED_ORIGINS` | `settings.py` |
| 401 en todas las peticiones | Token caducado o refresh fallando | Network del navegador + `/api/api/token/refresh/` |
| La imagen no se ve | `MEDIA_URL`/`MEDIA_ROOT` o el archivo no está en `media/` | `settings.py` y carpeta `media/` |
| Puertos ocupados | 8000, 4200 o 5435 ya en uso | Cambiar el mapeo o parar el otro servicio |

Y si algo huele a problema ya conocido, mirar §13 antes de tocar código.

### 12.8 Cuándo se añaden tests de algo ya existente

- Si una tarea toca código viejo sin tests, **no** es obligatorio cubrir todo ese código de golpe;
  sí es obligatorio añadir tests de lo que se modifica y de lo que podría romperse por el cambio.
- Cuando una tarea arregle un bug, se añade **primero el test que reproduce el fallo** y luego la
  corrección (así queda demostrado que el bug estaba ahí y que ya no está).

---

## 13. Decisiones pendientes del humano (NO ejecutar sin autorización)

Puntos detectados al leer el código y al escribir este documento. Son **para decidir**, no una
lista de tareas a ejecutar por iniciativa propia.

1. **Versionado de la API** (`/api/v1/`): decidir si se normaliza ahora (§11.1) o se mantiene el
   contrato actual.
2. **Artefactos versionados**: `retro-app/dist/`, `retro-api/media/` y `skills-lock.json` aparecen
   en el árbol; decidir si deben salir del control de versiones (añadir a `.gitignore`) o quedarse.
3. **`.env.example`**: crear una plantilla sin secretos para que el onboarding (§12.7) no dependa
   de copiar un `.env` real. Requiere autorización porque toca configuración.
4. **Archivos sin trackear en la API**: `backup.sql`, `restore_data.py` y `verify.py` (§11.18):
   decidir si se versionan (con `backup.sql` fuera por tamaño/datos), se documentan o se mueven a
   `docs/`/`scripts/`.
5. **Paginación**: decidir entre paginación en servidor (§11.12) o mantener el cliente, según el
   volumen real de datos esperado.
6. **JWT en `localStorage` vs cookie `HttpOnly`** (§11.15): decisión de arquitectura que afecta a
   los dos repos.
7. **Registro abierto** (`RegistroView` público, §11.6): decidir si se mantiene o se restringe.
8. **Despliegue**: cerrar qué proveedor se usa para cada repo (ya existen ramas
   `despliegue-render` y `despliegue-vercel`) y dejar por escrito sus variables de entorno.

---

## 14. Checklist rápido antes de dar una tarea por terminada

- [ ] Está dentro del plan aprobado y no toca nada fuera de su alcance.
- [ ] Respeta la estructura de carpetas (§2), las convenciones (§6) y los principios (§5.3).
- [ ] Consultas optimizadas, sin N+1 (§7.1) y con transacción donde toca (§7.3).
- [ ] Permisos explícitos, validación en el serializer y sin datos sensibles expuestos (§8).
- [ ] Tests añadidos y en verde (§6.4); si el cambio arregla un bug, existe el test que lo
      reproducía (§12.8).
- [ ] Compila: `npm run build` (frontend) y/o la API arranca sin errores.
- [ ] Si aplica: los cuatro estados de UI están resueltos (§12.5) y la accesibilidad mínima se
      cumple (§12.6).
- [ ] Si toca base de datos: migración nueva revisada, reversible y con backup previsto (§12.3).
- [ ] Sin `any`, sin `console.log`/`print()`, sin código comentado ni TODOs sin dueño (§6.5).
- [ ] He dicho al humano **cómo verificarlo** y he preguntado **"¿Todo bien?"**.
- [ ] **Confirmación recibida** → entonces (y solo entonces) escribo el documento de historial
      (con su rama y sus tests) y marco la tarea como completada en el plan.
- [ ] Si el cambio altera el contrato de la API, §5.2 de este archivo queda actualizado.
