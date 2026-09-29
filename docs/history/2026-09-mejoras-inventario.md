# Historial — Mejoras de RETRO_INVENTORY

Documento de historial del listado de tareas **"Mejoras de RETRO_INVENTORY"** (ver `docs/PLAN.md`).
Solo se anotan aquí las tareas **verificadas y confirmadas por el humano**.

- **Rama de trabajo:** `mejoras-inventario` (en `retro-api` y en `retro-app`)
- **Repos afectados:** `retro-api` (backend) y `retro-app` (frontend)
- **Creado:** septiembre de 2026

---

## A1. Arreglar el login (autenticación por email)

- **¿Qué realiza?:** hace que el endpoint de login (`POST /api/api/token/`) acepte **email +
  contraseña** y devuelva los tokens JWT (`access` y `refresh`). Antes esperaba el campo `username`
  (valor por defecto de SimpleJWT), por lo que el frontend —que envía `email`— recibía un error 400
  y la aplicación no dejaba entrar a ningún usuario normal. Además, ahora se guarda la fecha del
  último acceso correcto en el usuario (`last_login`).

- **¿Por qué?:** la aplicación era **inutilizable desde el frontend**: el modelo `User` usa el email
  como identificador (`USERNAME_FIELD = 'email'`) y el formulario de login pide email, pero
  SimpleJWT buscaba `username`. El único modo de entrar era el panel de administración de Django,
  no la app. Sin esto, ninguna otra tarea se puede dar por buena desde la interfaz.

- **Dónde verlo:**
  - `retro-api/core/settings.py` (líneas 149-160: configuración `SIMPLE_JWT`, con
    `'USERNAME_FIELD': 'email'` en la línea 154 y `'UPDATE_LAST_LOGIN': True` en la 158)
  - `retro-api/inventory/tests/test_a1_login.py` (líneas 1-76: tests del login; los cuatro casos
    están en las líneas 46, 58, 66 y 72)
  - `retro-api/inventory/tests/__init__.py` (paquete de tests del inventario)

- **Cómo verificar:**
  1. **En la app (lo principal):** reiniciar la API con `docker compose restart api` dentro de
     `retro-api`, abrir `http://localhost:4200`, introducir **email y contraseña** y pulsar
     "Entrar". Debe entrar al dashboard con las tarjetas de totales.
  2. **Tests automáticos:**
     `docker compose exec api python manage.py test inventory.tests.test_a1_login`
     → debe terminar en `Ran 4 tests` / `OK`.
  3. **Servidor en vivo:**
     `curl -s -X POST http://localhost:8000/api/api/token/ -H "Content-Type: application/json" -d "{}"`
     → debe responder pidiendo `email` y `password` (antes pedía `username`).
  4. **Rechazo de credenciales malas:** email inexistente o contraseña incorrecta → `401`.

- **Tests añadidos:** `retro-api/inventory/tests/test_a1_login.py`
  - `test_login_con_email_devuelve_tokens` (línea 46): login correcto devuelve `access` y `refresh`.
  - `test_el_token_abre_un_endpoint_protegido` (línea 58): el token sirve para autenticarse.
  - `test_email_inexistente_no_entra` (línea 66): email desconocido → 401.
  - `test_contrasena_incorrecta_no_entra` (línea 72): contraseña incorrecta → 401.

- **Rama de trabajo:** `mejoras-inventario` (`retro-api`).

- **Archivos tocados:** `core/settings.py` (modificado),
  `inventory/tests/test_a1_login.py` y `inventory/tests/__init__.py` (nuevos).

- **Hallazgo durante la verificación (no corregido, fuera del alcance de A1):** los endpoints del
  inventario responden **200 sin token**. Comprobado con `GET /api/consoles/` sin autenticación.
  Causa: los ViewSets no declaran `permission_classes` y DRF usa su valor por defecto (permitir a
  cualquiera). Se corrige en la tarea **E4** del plan, con su propio test. Está detallado en
  `AGENTS.md` §11.5 (seguridad).

- **Estado:** ✅ Completada — confirmada por el humano el 29 de septiembre de 2026.

---

## D1. Precio del artículo y precio total

- **¿Qué realiza?:** separa el precio de un artículo en **dos campos**:
  - **`price`** → precio del artículo (lo que costaba la pieza). Ya existía y **no cambia de
    significado ni de valor**: los datos anteriores se quedan como están.
  - **`total_price`** (nuevo) → lo que costó de verdad, con envío, comisiones y gastos incluidos.

  Reglas: si al guardar no se indica el total, se copia el precio del artículo; y si se indica un
  total **menor** que el precio del artículo, la API lo rechaza.

- **¿Por qué?:** hasta ahora solo existía `price` y no quedaba claro si era el precio del anuncio o
  lo que se pagó al final. Con dos campos se puede saber **el valor de la colección** (precio de
  cada pieza) y **lo que se ha invertido de verdad** (total pagado). Se descartó a propósito
  desglosar envío y comisiones por separado (decisión del humano, 29/09/2026): con dos campos basta
  y no obliga a recordar más datos en cada alta.

- **Dónde verlo:**
  - `retro-api/inventory/models/Base.py` (línea 97: etiqueta del campo `price`; líneas 100-109: campo
    `total_price`, definido en `ItemBase`, así que lo heredan Console, Game y Accessory)
  - `retro-api/inventory/migrations/0013_accessory_total_price_console_total_price_and_more.py`
    (líneas 6-30: relleno de los datos existentes con `RunPython`; 33-79: operaciones de esquema)
  - `retro-api/inventory/api/serializers/console.py`, `game.py` y `accessory.py` (línea 25: el campo
    en la lista de la API; 31-48: la validación del total)
  - `retro-api/inventory/api/views/view_console.py`, `view_game.py` y `view_accessory.py` (línea 11:
    `total_price` añadido a `ordering_fields`, para poder ordenar por total)
  - `retro-api/inventory/admin.py` (líneas 16, 20, 25, 29, 34 y 38: las dos columnas visibles y
    editables en las tres secciones)
  - `retro-api/inventory/tests/test_d1_precio_total.py` (líneas 51, 59, 70, 80, 89 y 102: los 6 tests)

- **Cómo verificar:**
  1. **Tests automáticos:**
     `docker compose exec api python manage.py test inventory.tests.test_d1_precio_total`
     → `Ran 6 tests` / `OK`. Y la suite completa: `docker compose exec api python manage.py test`
     → `Ran 10 tests` / `OK`.
  2. **La API en vivo** ya devuelve el campo:
     `curl -s http://localhost:8000/api/consoles/` → cada artículo tiene `"total_price"`.
  3. **Ordenación:** `curl -s "http://localhost:8000/api/consoles/?ordering=-total_price"` → 200.
  4. **Regla del total:** enviar `price: 30` y `total_price: 20` → la API responde **400** con
     `total_price: "El total no puede ser menor que el precio del artículo."`.
  5. **Relleno de datos** (comprobado en la base de datos real el 29/09/2026): 50 artículos con
     precio, 50 con total y **50 con total = precio**; ninguna diferencia.
  6. **En la app** (parte de frontend, detallada en `retro-app/docs/history/`): el formulario pide
     las dos cantidades, el detalle muestra las dos y la lista usa el total.

- **Tests añadidos:** `retro-api/inventory/tests/test_d1_precio_total.py`
  - `test_sin_total_se_copia_el_precio` (51): sin total, se copia el precio del artículo.
  - `test_total_mayor_que_el_precio_se_guarda` (59): con gastos, se guarda el total indicado.
  - `test_total_menor_que_el_precio_se_rechaza` (70): total menor → 400.
  - `test_total_igual_al_precio_se_acepta` (80): valores iguales → válido.
  - `test_articulo_antiguo_sin_total_sigue_funcionando` (89): un artículo anterior al campo se lee
    sin errores.
  - `test_se_puede_ordenar_por_total` (102): la API acepta `?ordering=-total_price`.

- **Rama de trabajo:** `precio-y-compra` (en `retro-api` y en `retro-app`).

- **Archivos tocados en el backend:** `inventory/models/Base.py`,
  `inventory/migrations/0013_...py` (nueva), los 3 serializers, los 3 viewsets, `inventory/admin.py`
  y `inventory/tests/test_d1_precio_total.py` (nuevo). **En el frontend, 17 archivos** (ver el
  historial de `retro-app`).

- **Fallo encontrado y corregido durante esta tarea (venía de A1):** `python manage.py test` **no
  ejecutaba la suite completa**. Existían a la vez `inventory/tests.py` (el archivo vacío que genera
  Django) y `inventory/tests/` (el paquete creado en A1), y Django fallaba con
  `ImportError: 'tests' module incorrectly imported`. No se había detectado porque en A1 y B1 se
  ejecutaban tests concretos, no todos. Se eliminó el archivo vacío `inventory/tests.py`; ahora la
  suite completa corre y pasa.

- **Nota de diseño:** el campo se añadió a `ItemBase` (el modelo abstracto), por lo que una sola
  migración crea la columna en las tres tablas (`console`, `game`, `accessory`). El relleno es
  **idempotente** (solo toca filas con el total vacío) y tiene operación inversa documentada, según
  `AGENTS.md` §12.3.

- **Estado:** ✅ Completada — confirmada por el humano el 29 de septiembre de 2026.
