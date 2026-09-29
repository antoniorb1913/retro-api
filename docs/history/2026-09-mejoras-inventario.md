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
  cualquiera). Se corrige en la tarea **E4** del plan, con su propio test.

- **Estado:** ✅ Completada — confirmada por el humano el 29 de septiembre de 2026.
