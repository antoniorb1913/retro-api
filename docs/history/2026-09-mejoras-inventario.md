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

---

## D2. Enlace de compra y botón "Ver compra"

- **¿Qué realiza?:** añade un campo **`purchase_url`** ("Enlace de compra") a consolas, juegos y
  accesorios. En la ficha del artículo aparece un botón **"Ver compra"** que abre ese enlace **en
  pestaña nueva**. El botón solo se muestra si el artículo tiene enlace.

- **¿Por qué?:** al catalogar un artículo comprado de segunda mano se pierde la referencia del
  anuncio (precio de mercado, fotos, estado descrito, vendedor). Guardando el enlace se puede
  volver a consultar. Se descartó a propósito un comparador automático de precios de
  Wallapop/Vinted (no tienen API pública y hacer scraping no es aceptable), decisión del humano.

- **Decisión de diseño:** se guarda el enlace del **anuncio público**, no el de la página del
  pedido: los pedidos suelen requerir sesión iniciada y caducan, así que dejarían de funcionar.

- **Dónde verlo:**
  - `retro-api/inventory/models/Base.py` (líneas 110-117: campo `purchase_url`, `URLField` de 500
    caracteres, opcional; definido en `ItemBase`, así que lo heredan los tres modelos)
  - `retro-api/inventory/migrations/0014_accessory_purchase_url_console_purchase_url_and_more.py`
    (líneas 13, 18 y 23: añade la columna a las tres tablas; no hay datos que migrar)
  - `retro-api/inventory/api/serializers/console.py`, `game.py` y `accessory.py` (línea 27: el campo
    en la lista de la API; 52-66: la validación del enlace; 1-3: el import de `urlparse`)
  - `retro-api/inventory/admin.py` (líneas 22, 35 y 48: el campo en los formularios del admin)
  - `retro-api/inventory/tests/test_d2_enlace_compra.py` (8 tests) y
    `retro-api/inventory/tests/test_admin_inventario.py` (3 tests, ver el fallo encontrado abajo)

- **Cómo verificar:**
  1. **Tests de la tarea:**
     `docker compose exec api python manage.py test inventory.tests.test_d2_enlace_compra`
     → `Ran 8 tests` / `OK`.
  2. **Tests del admin:** `docker compose exec api python manage.py test inventory.tests.test_admin_inventario`
     → `Ran 3 tests` / `OK`.
  3. **Suite completa:** `docker compose exec api python manage.py test` → `Ran 21 tests` / `OK`.
  4. **La API en vivo:** `curl -s http://localhost:8000/api/consoles/` → cada artículo tiene
     `"purchase_url"`.
  5. **Rechazo de enlaces peligrosos** (comprobado por curl el 29/09/2026):
     `curl -X POST http://localhost:8000/api/consoles/ -H "Content-Type: application/json" -d '{"name":"x","purchase_url":"javascript:alert(1)"}'`
     → **HTTP 400**.
  6. **URL demasiado larga** (541 caracteres) → **HTTP 400**, no un error 500.
  7. **El admin:** las seis páginas de inventario (`/admin/inventory/console/`, `/game/`,
     `/accessory/` y sus `add/`) responden 200 y el campo se puede rellenar desde la ficha.
  8. **En la app** (parte de frontend, detallada en `retro-app/docs/history/`): el formulario pide el
     enlace y la ficha muestra el botón.

- **Tests añadidos:**
  - `inventory/tests/test_d2_enlace_compra.py` (8):
    - `test_guarda_un_enlace_valido` (48): un enlace normal se guarda y se devuelve.
    - `test_el_enlace_es_opcional` (56): se puede crear sin enlace.
    - `test_acepta_http_y_https` (63): los dos esquemas web válidos se aceptan.
    - `test_rechaza_esquemas_peligrosos` (70): `javascript:`, `data:` y `file:` → 400.
    - `test_rechaza_lo_que_no_es_una_url` (87): texto suelto → 400.
    - `test_rechaza_un_enlace_demasiado_largo` (94): más de 500 caracteres → 400.
    - `test_el_enlace_se_puede_editar_y_vaciar` (104): se cambia y se borra con PATCH.
    - `test_aparece_en_el_listado` (126): el listado devuelve el campo.
  - `inventory/tests/test_admin_inventario.py` (3): que los campos declarados en el admin existan
    de verdad en el modelo, que las seis páginas abran y que el enlace esté en el formulario.

- **Seguridad (lo importante de esta tarea):** un enlace que se pinta en pantalla es un punto de
  ataque, así que:
  - El backend **solo** acepta `http` y `https`. Cualquier otro esquema se rechaza con 400
    (`javascript:alert(1)`, `data:text/html,<script>…`, `file:///etc/passwd`).
  - El frontend abre el enlace con `target="_blank"` **y `rel="noopener noreferrer"`**, que impide
    que la página destino manipule la aplicación desde `window.opener`.
  - La longitud máxima (500) se valida con un 400 claro en vez de romper en la base de datos.

- **Fallo encontrado y corregido durante esta tarea (importante):** al añadir el campo al admin se
  declaró por error la lista de campos de `Accessory` **con `edition`**, un campo que ese modelo no
  tiene (se copió del bloque de `Console`). Eso **no lo detecta `manage.py check`**: Django lanza
  `FieldError: Unknown field(s) (edition) specified for Accessory` al **abrir** la página del admin,
  es decir, un 500 en la cara del usuario y solo en producción si nadie entra antes. Se detectó
  abriendo las páginas del admin una a una. Se corrigió y se añadió el test
  `test_los_formularios_declarados_usan_campos_reales`, **comprobado al revés**: reintroduciendo el
  fallo a propósito, el test falla con `'edition' : Accessory declara campos que no existen`.

- **Rama de trabajo:** `enlace-compra` (en `retro-api` y en `retro-app`).

- **Archivos tocados en el backend:** `inventory/models/Base.py`, los 3 serializers,
  `inventory/admin.py`, la migración 0014 (nueva), `inventory/tests/test_d2_enlace_compra.py`
  (nuevo) y `inventory/tests/test_admin_inventario.py` (nuevo). **En el frontend, 10 archivos**
  (ver el historial de `retro-app`).

- **Estado:** ✅ Completada — confirmada por el humano el 29 de septiembre de 2026.

---

## E4. Permisos explícitos en los endpoints (la API estaba abierta)

- **¿Qué realiza?:** cierra la API. Hasta esta tarea, **cualquier petición sin token se atendía**:
  se podía leer, crear, editar y **borrar** el inventario sin estar autenticado. Ahora los cinco
  recursos del inventario (consolas, juegos, accesorios, imágenes y componentes) exigen token y
  responden **401** sin él. Lo único que sigue abierto es el login/refresh de token.

- **¿Por qué?:** es el agujero de seguridad más grave que tenía el proyecto y estaba confirmado
  desde la tarea A1 (`AGENTS.md` §11.5). No era una sospecha: se comprobó con `curl` que
  `GET /api/consoles/` devolvía **200 sin autenticación**, y `DELETE` **borraba** registros.

- **La causa raíz:** en `core/settings.py`, el bloque `REST_FRAMEWORK` declaraba
  `DEFAULT_AUTHENTICATION_CLASSES` pero **no** `DEFAULT_PERMISSION_CLASSES`. Cuando DRF no
  encuentra ese ajuste, **permite el paso a todo**. Por eso ninguna vista estaba protegida, aunque
  el token existiera y funcionara.

- **Dónde verlo:**
  - `retro-api/core/settings.py` (líneas 150-152: `DEFAULT_PERMISSION_CLASSES` con
    `IsAuthenticated`; 146-149: el comentario que explica el porqué)
  - `retro-api/inventory/api/views/view_console.py` (línea 2: import; 9: `permission_classes`)
  - `retro-api/inventory/api/views/view_game.py` (2 y 9), `view_accessory.py` (2 y 9),
    `view_image.py` (2 y 11) y `view_mcomponent.py` (2 y 8)
  - `retro-api/user/api/views.py` (línea 4: import de `AllowAny`; 11: la única vista abierta)
  - `retro-api/inventory/tests/test_e4_permisos.py` (los 10 tests)

- **Decisión de diseño (denegar por defecto, `AGENTS.md` §8.1):** el cierre se hace **en dos
  niveles**:
  1. **Global**, con `DEFAULT_PERMISSION_CLASSES`: cualquier vista **futura** nace protegida. Si
     algún día se olvida declarar permisos en una vista nueva, el fallo será "no deja entrar" en
     vez de "lo deja todo abierto".
  2. **Por vista**, declarando `permission_classes = [IsAuthenticated]` en cada ViewSet: así el
     archivo dice por sí solo qué permite, sin tener que ir a `settings.py` a averiguarlo.

- **Cómo verificar:**
  1. **Tests de la tarea:** `docker compose exec api python manage.py test inventory.tests.test_e4_permisos`
     → `Ran 10 tests` / `OK`.
  2. **Suite completa:** `docker compose exec api python manage.py test` → `Ran 31 tests` / `OK`.
  3. **El agujero existía de verdad:** los mismos tests se ejecutaron **antes** de aplicar el
     arreglo y **fallaron 9 de 10**. Resultados reales de esa ejecución:
     - `/api/images/` y `/api/components/` devolvían **200** sin token.
     - Subir una imagen sin token devolvía **400** (no 401): es decir, la petición **llegaba y se
       validaba**. Cualquiera podía llenar el servidor de archivos sin tener cuenta.
     - `test_sin_token_no_se_puede_borrar` fallaba: sin token se borraban registros.
  4. **Contra la API en vivo** (comprobado el 29/09/2026 con `curl`):
     los cinco `GET /api/<recurso>/` sin token → **401**; con token válido → **200**.
  5. **El borrado, que es el caso grave:** `DELETE /api/consoles/<id>/` sin token → **401**, y el
     registro **sigue existiendo** (comprobado leyéndolo después con token). Con token → **204**.
  6. **Lo que debe seguir abierto:** `GET /api/docs/` → 200, `GET /api/schema/` → 200.
  7. **En la aplicación** (comprobado por el humano el 29/09/2026): con la sesión iniciada todo
     funciona igual (listas, detalles, fotos, crear, editar, subir imagen y borrar).

- **Tests añadidos:** `retro-api/inventory/tests/test_e4_permisos.py` (10):
  - `test_sin_token_no_se_puede_leer_ningun_recurso` (64): los 5 recursos → 401.
  - `test_sin_token_no_se_puede_crear` (83): crear sin token → 401 y **nada se guarda**.
  - `test_sin_token_no_se_puede_editar` (94): editar sin token → 401 y **el dato no cambia**.
  - `test_sin_token_no_se_puede_borrar` (106): el caso más grave → 401 y **el registro sigue ahí**.
  - `test_sin_token_no_se_puede_subir_una_imagen` (120): subida sin token → 401.
  - `test_con_token_se_puede_leer_escribir_y_borrar` (136): ciclo completo con token (no se cerró
    de más).
  - `test_con_token_funcionan_los_cinco_recursos` (167).
  - `test_un_token_invalido_tampoco_entra` (182): un token falso se rechaza igual que no llevarlo.
  - `test_el_login_sigue_abierto` (193) y `test_el_refresh_sigue_abierto` (205).

- **Hallazgo secundario (no corregido, es decisión aparte):** `RegistroView` **no está conectada a
  ninguna ruta**. Se comprobó que `POST /api/register/` devuelve **404** y que la vista no aparece
  en el listado de rutas de Django: es **código muerto**. No es que el registro esté abierto, es
  que no existe. Se ha dejado tal cual (quitarla o conectarla es la decisión §13.7 del `AGENTS.md`)
  y se añadió un comentario en `user/api/views.py` avisando de ello. Por este motivo el test del
  registro que se había previsto **no se incluyó**: probar una ruta que no existe no aporta nada.

- **Nota sobre las imágenes:** se comprobó que la aplicación pinta las fotos con
  `<img src="/media/...">`, es decir, el navegador las pide a `/media/` y **no** a la API. Por eso
  cerrar la API **no rompe las imágenes**. Si algún día se sirven por la API, habría que revisarlo.

- **Rama de trabajo:** `seguridad-calidad` (`retro-api`). Esta tarea es solo de backend; en
  `retro-app` no se tocó nada.

- **Archivos tocados:** `core/settings.py`, los 5 `inventory/api/views/view_*.py`,
  `user/api/views.py` y `inventory/tests/test_e4_permisos.py` (nuevo).

- **Estado:** ✅ Completada — confirmada por el humano el 29 de septiembre de 2026.

---

## E5. Validar el destino al subir imágenes (se aceptaban artículos que no existen)

- **¿Qué realiza?:** cierra el endpoint de imágenes. Antes, al subir una foto:
  1. Se aceptaba **cualquier `object_id`**, aunque no existiera ningún artículo con ese id: la API
     respondía **201** y creaba una **carpeta fantasma** en el disco
     (`media/consoles/unknown-999999/…`).
  2. Un `content_type_model` inventado **no** daba un error controlado: reventaba con
     `DoesNotExist` y Django devolvía una **página 500 con la traza completa** (rutas internas y
     versiones incluidas).
  3. Se podía decir que la foto pertenece a **cualquier** modelo de la app `inventory`, incluidos
     los que no deben llevar imágenes, como `missingcomponent` (el catálogo de piezas).

  Ahora el destino tiene que ser un **artículo real** y de uno de los tres tipos permitidos
  (consola, juego o accesorio); en cualquier otro caso la API responde **400 con un mensaje claro**
  y **no escribe nada** en el disco.

- **¿Por qué?:** es la continuación directa de E4. Desde E4 solo el dueño puede subir archivos, pero
  **el propio dueño** podía llenar el servidor de imágenes huérfanas sin querer (un id equivocado
  basta), y esas imágenes no se pueden ni ver ni borrar desde la aplicación porque no cuelgan de
  ningún artículo. Además, el 500 con traza es una fuga de información interna.

- **Dónde verlo:**
  - `retro-api/inventory/api/serializers/image.py` (línea 20: la lista cerrada
    `MODELOS_CON_IMAGENES`; 22-23: el mensaje único; 26-58: el mixin con la validación compartida;
    61 y 87: los dos serializers que ahora la heredan)
  - `retro-api/inventory/tests/test_e5_imagenes.py` (los 10 tests)

- **Decisión de diseño (una sola pieza para los dos serializers):** el fallo de raíz fue que
  **solo uno de los dos** serializers validaba, y el que se usaba al subir (`ImageUploadSerializer`)
  era justo el que no. La validación vive ahora en un **mixin** que heredan los dos, así que es
  **físicamente imposible** que uno se quede sin ella. Se aplica al principio del proyecto
  (`AGENTS.md` §5.3.3: una responsabilidad por pieza) sin duplicar código.

- **Decisión de diseño (lista cerrada en vez de `try/except`):** el 500 se elimina **por
  construcción**, no tapando el síntoma. Al declarar `content_type_model` como `ChoiceField`, DRF
  rechaza cualquier valor fuera de la lista **antes** de llegar al código que consultaba la base de
  datos. Un `try/except DoesNotExist` habría dejado el agujero abierto para el siguiente caso no
  previsto.

- **Cómo verificar:**
  1. **Tests de la tarea:** `docker compose exec api python manage.py test inventory.tests.test_e5_imagenes`
     → `Ran 10 tests` / `OK`.
  2. **Suite completa:** `docker compose exec api python manage.py test` → `Ran 41 tests` / `OK`.
  3. **El agujero existía de verdad:** los mismos tests se ejecutaron **antes** de aplicar el
     arreglo y **fallaron 9 de 10**. Resultados reales de esa ejecución:
     - `object_id=999999` → **201**, con la ruta `media/consoles/unknown-999999/foto.webp`.
     - `content_type_model=noexiste` → **ERROR** `ContentType.DoesNotExist` (el 500 con traza).
     - `content_type_model=missingcomponent` → **201**, creando `media/missingcomponents/caja-1/`.
  4. **Contra la API en vivo** (comprobado el 29/09/2026 con `curl` y un token real):
     los tres casos inválidos → **400** con mensaje claro; una subida correcta → **201**.
  5. **En la aplicación** (comprobado por el humano el 29/09/2026): subir una foto desde el
     formulario de un artículo sigue funcionando igual.

- **Tests añadidos:** `retro-api/inventory/tests/test_e5_imagenes.py` (10). Usan una **carpeta
  temporal** de `media/` (`override_settings`), así que no ensucian los archivos reales:
  - `test_una_subida_correcta_funciona` (113): la subida válida sigue dando 201 y guarda el archivo.
  - `test_se_puede_subir_a_los_tres_tipos` (129): consolas, juegos y accesorios.
  - `test_rechaza_un_object_id_que_no_existe` (147): el fallo principal → 400 y sin crear la fila.
  - `test_un_object_id_inexistente_no_deja_archivos` (158): el rechazo **no deja basura** en disco.
  - `test_el_object_id_debe_ser_del_tipo_indicado` (171): un id que existe pero es de otro tipo.
  - `test_rechaza_un_content_type_model_inventado_sin_reventar` (186): el 500 pasa a ser 400.
  - `test_rechaza_un_modelo_que_no_debe_llevar_fotos` (196): `missingcomponent` se rechaza.
  - `test_rechaza_modelos_que_no_son_de_inventario` (206): `user`, `contenttype`, `session`.
  - `test_rechaza_si_falta_el_modelo` (213): el destino es obligatorio.
  - `test_el_serializer_de_lectura_tambien_valida` (229): el otro serializer también valida.

- **Hallazgo durante la tarea (datos del humano, ya resuelto):** revisando las imágenes se
  detectaron **2 filas que apuntaban a archivos inexistentes** en el accesorio *"Demo Winter
  Releases '98"* (id 6), subidas el 03/07/2026: `accessorys/demo-winter-releases-98-6/DISCO.webp` y
  `.../demo_Winter_Releases_98.webp`. **La carpeta entera faltaba en el disco** (comprobado desde el
  host y desde el contenedor). Se avisó al humano, que **borró esas dos imágenes y subió una nueva**
  desde la aplicación. Estado final comprobado: **247 imágenes y 0 referencias rotas**. Este caso es
  justo el tipo de problema que E5 evita que se repita (aunque aquel venía de antes: los archivos se
  borraron del disco sin pasar por la aplicación).

- **Nota:** no hizo falta **ninguna migración** (F1 ni cambios de esquema): todo el trabajo es
  validación en el serializer, tal como pedía el plan.

- **Rama de trabajo:** `seguridad-calidad` (`retro-api`). Como E4, es solo de backend; en
  `retro-app` no se tocó nada.

- **Archivos tocados:** `inventory/api/serializers/image.py` y
  `inventory/tests/test_e5_imagenes.py` (nuevo).

- **Estado:** ✅ Completada — confirmada por el humano el 29 de septiembre de 2026.

---

## E6. Freno de intentos en el login y en la subida de imágenes

- **¿Qué realiza?:** limita cuántas veces se pueden intentar ciertas acciones:
  - **Login** (`POST /api/api/token/`): **10 intentos por minuto**. A partir de ahí, **429** (Too
    Many Requests) en vez de seguir atendiendo.
  - **Refresco de token** (`POST /api/api/token/refresh/`): 10 por minuto, con su propio contador.
  - **Subida de imágenes** (`POST /api/images/`): **20 por hora**, también con contador propio.

  Los contadores son **independientes**: gastar intentos de login no afecta a las subidas.

- **¿Por qué?:** era el último de los tres agujeros de seguridad serios del plan. Sin límite, se
  pueden probar contraseñas a miles por minuto con un programa (fuerza bruta). Los otros dos ya se
  cerraron: E4 (la API estaba abierta a cualquiera) y E5 (la subida aceptaba destinos falsos).

- **Dónde verlo:**
  - `retro-api/core/settings.py` (líneas 153-168: `DEFAULT_THROTTLE_CLASSES` y
    `DEFAULT_THROTTLE_RATES` con los tres límites y el porqué de cada número)
  - `retro-api/user/api/throttles.py` (línea 14: `ThrottleConExencionStaff`, con la explicación de
    hasta dónde llega la exención del dueño)
  - `retro-api/user/api/views_token.py` (línea 15: `LoginConLimiteView`; 24:
    `RefreshConLimiteView`) — heredan de las vistas de SimpleJWT solo para añadirles el freno
  - `retro-api/user/api/router.py` (líneas 6-7: se usan esas vistas en vez de las de la librería)
  - `retro-api/inventory/api/views/view_image.py` (líneas 13-17: el freno de subidas)
  - `retro-api/inventory/tests/test_e6_throttling.py` (los 10 tests)

- **Decisión de diseño (los números):** se eligieron mirando el uso real, no al azar:
  - **10/min en login**: una persona se equivoca 1 o 2 veces, así que no le afecta; a un programa
    que prueba contraseñas lo para en seco. Además, la suite de tests hace 7 logins en 3 segundos,
    así que el límite no rompe las pruebas.
  - **20/hora en subidas**: cada imagen se convierte a WebP y se escribe en disco. Una sesión
    normal de catalogar no llega a esa cifra.
  - Los números viven en `settings.py` (y no en el código de las vistas) para poder ajustarlos sin
    tocar lógica.

- **Decisión de diseño (la exención del dueño):** en una aplicación de un solo usuario, un límite
  bajo hace que el propio dueño se bloquee mientras prueba. Por eso las vistas usan
  `ThrottleConExencionStaff`, que deja pasar a `is_staff`. **Importante**: esa exención solo
  funciona donde la petición ya va autenticada (la subida de imágenes, que manda el token). **En el
  login no puede funcionar** y no es un fallo del código: cuando alguien pide un token todavía no
  ha demostrado quién es, así que DRF ve un usuario anónimo y cuenta el límite **por IP**. Es decir,
  el dueño también se frena si se pasa al entrar; con 10/min que se recuperan solos, en la práctica
  no molesta. Queda documentado en el código y con un test que fija ese comportamiento
  (`test_el_login_tambien_frena_al_dueno`) para que nadie lo "arregle" creyendo que es un error.

- **Cómo verificar:**
  1. **Tests de la tarea:** `docker compose exec api python manage.py test inventory.tests.test_e6_throttling`
     → `Ran 10 tests` / `OK`.
  2. **Suite completa:** `docker compose exec api python manage.py test` → `Ran 51 tests` / `OK`.
  3. **El agujero existía de verdad:** los tests se ejecutaron **antes** de aplicar el freno y
     **fallaron 5 de 7**. Resultados reales: 6 intentos de login seguidos → `[200, 200, 200, 200,
     200, 200]` (ninguno frenado) y 5 subidas seguidas → `[201, 201, 201, 201, 201]`.
  4. **Contra la API en vivo** (comprobado el 30/09/2026, 12 intentos con contraseña mala):
     `401` en los 10 primeros y **`429` en el 11 y el 12**.
  5. **El freno es temporal, no un bloqueo:** pasados 70 segundos, un login correcto vuelve a
     responder **200** y con su token se leen las consolas (**200**).
  6. **Lo que no se ha roto:** `/api/docs/` sigue en 200 y `/api/consoles/` sin token sigue en 401.

- **Tests añadidos:** `retro-api/inventory/tests/test_e6_throttling.py` (10):
  - `test_pasarse_de_intentos_en_el_login_devuelve_429`
  - `test_no_frena_antes_de_pasarse` (no se frena de más)
  - `test_el_freno_es_temporal_no_un_bloqueo`
  - `test_un_usuario_normal_se_bloquea`
  - `test_entrar_dentro_del_limite_funciona`
  - `test_el_refresh_tiene_su_propio_limite`
  - `test_el_login_tambien_frena_al_dueno` (deja escrito el comportamiento real de la exención)
  - `test_el_dueno_no_se_frena_al_subir_imagenes` (la exención donde sí funciona)
  - `test_la_subida_de_imagenes_tiene_su_propio_limite`
  - `test_subir_imagenes_no_gasta_el_limite_del_login`

  Los límites de los tests se **leen del freno real** (no se escriben a mano), así que si algún día
  se ajustan los números en `settings.py`, los tests siguen valiendo.

- **Aprendizaje importante al escribir los tests (documentado en el archivo):** los límites de DRF
  **no se pueden cambiar con `override_settings`**. DRF los lee **una sola vez**, al cargar su
  módulo (`SimpleRateThrottle.THROTTLE_RATES` es un atributo de clase). El primer intento de test
  parecía comprobar un límite de 3/min cuando en realidad se aplicaba el de producción, y daba un
  "no frena" que no significaba nada. Además, `override_settings(CACHES=…)` **no aísla** el freno:
  lo que aísla de verdad es limpiar la caché en `setUp`, porque los contadores no se borran entre
  tests. Las dos trampas quedaron explicadas en la cabecera del archivo de tests.

- **Fallo encontrado y corregido durante esta tarea:** al crear `user/tests/` para un test temporal
  se reprodujo el **choque de nombres** que ya se corrigió en D1 (`user/tests.py` conviviendo con
  `user/tests/`): `ImportError: 'tests' module incorrectly imported`. Se comprobó que la carpeta
  solo contenía el `__init__.py` vacío, se restauró `user/tests.py` y se eliminó la carpeta vacía.

- **Deuda anotada (frontend, NO se tocó):** el login de la aplicación muestra **"Credenciales
  inválidas"** ante cualquier error ([`login.component.ts`, líneas 32-35](retro-app/src/app/features/auth/login.component.ts#L32)):
  ```ts
  error: () => { this.error.set('Credenciales inválidas'); }
  ```
  Desde E6, la API puede responder **429** por demasiados intentos, y en ese caso el mensaje sería
  engañoso (la contraseña puede ser correcta). Se propone como tarea corta aparte.

- **Rama de trabajo:** `seguridad-calidad` (`retro-api`). Es una tarea de backend; en `retro-app`
  no se tocó nada.

- **Archivos tocados:** `core/settings.py`, `user/api/router.py`,
  `inventory/api/views/view_image.py`, `user/api/throttles.py` (nuevo),
  `user/api/views_token.py` (nuevo) e `inventory/tests/test_e6_throttling.py` (nuevo).

- **Estado:** ✅ Completada — confirmada por el humano el 30 de septiembre de 2026.
