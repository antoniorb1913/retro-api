# PLAN — Mejoras de RETRO_INVENTORY

> Estado: **propuesta**, pendiente de tu OK. No se ha escrito ni una línea de código.
> Los estados de cada tarea se actualizan **solo** cuando el humano confirma (§9.2 del `AGENTS.md`).

- **Objetivo:** completar la app (frontend a la par del backend), arreglar lo que está roto y dejar
  la base sólida (tests, seguridad, rendimiento) para seguir creciendo sin romper nada.
- **Alcance:** ambos repos (`retro-api` y `retro-app`).
- **Origen del listado:** mezcla de las mejoras pedidas por el humano (tienda, funda, filtros,
  desglose de precio, enlace de compra) y de los hallazgos de la lectura inicial (`AGENTS.md` §11).
  En negrita, las que aportó el humano.

## Decisiones tomadas para este plan (ajustables si no te valen)

1. **Precio**: `price` sigue siendo el **total** de lo que costó el artículo (artículo + envío +
   servicio). Se añaden dos campos nuevos (`shipping_cost`, `fees`) que por defecto son 0, así que
   **los datos que ya tienes no se tocan** y siguen cuadrando.
2. **Campo tienda**: se añade la opción `Otro / No especificado` a la lista de tiendas y se
   conserva el valor por defecto. El `'-'` que ya existe en la base de datos se deja como está y se
   pinta como "—" en la interfaz (no se tocan datos existentes).
3. **Filtros**: se guardan en la **URL** (`/consoles?search=ps2&platform=PS2&ordering=-price&page=2`)
   para que el botón "atrás" del navegador los recupere y la URL se pueda compartir.
4. **Comparador de precios (Wallapop/Vinted)**: **descartado** por decisión del humano (sin API
   pública). No se hace scraping.
5. **Enlace de compra**: el humano pega el enlace en el formulario y la app muestra un botón
   **"Ver compra"** que lo abre en pestaña nueva. Sin conexiones automáticas a plataformas.

- **Criterio de aceptación global:** al terminar todo el plan, la app se puede usar de principio a
  fin con un usuario normal (no solo el admin), muestra todos los datos que la API ya devuelve,
  conserva los filtros al navegar, refleja el coste real de cada artículo, y cada cambio está
  cubierto por tests.

## Bloques

- **Bloque A — Lo que está roto** (sin esto la app no es usable de verdad)
- **Bloque B — Recuperar lo que ya existe** (datos que la API ya manda y el frontend ignora)
- **Bloque C — Mejoras de uso diario** (filtros)
- **Bloque D — Mejoras de valor** (precio y enlace de compra)
- **Bloque E — Base sólida** (tests y seguridad, en trozos pequeños)
- **Bloque F — Mantenimiento barato**

## Tareas

### Bloque A — Lo que está roto

- [x] **A1. Arreglar el login (email)** · repo: `retro-api` · depende de: —
  Endpoint que acepta `email` + `password` y devuelve los tokens JWT, sin romper el frontend actual.
  ✅ **Completada el 29/09/2026** — doc: `retro-api/docs/history/2026-09-mejoras-inventario.md`
- [x] **A2. Verificar el flujo de login de punta a punta** · repo: `ambos` · depende de: A1
  Entrar desde `http://localhost:4200`, que el token se guarde, que las rutas protegidas carguen y
  que al cerrar sesión vuelva al login.
  ✅ **Completada el 29/09/2026** — doc: `retro-app/docs/history/2026-09-mejoras-inventario.md`
  (Verificado por el humano: entrar, recargar con F5, cerrar sesión y no poder volver a `/games`
  sin sesión. Sin cambios de código: solo verificación.)
- [ ] **A3. Normalizar la ruta de autenticación** · repo: `ambos` · depende de: A2
  Hoy el login está en `/api/api/token/` (el `api` duplicado, porque el router de `user` añade su
  propio prefijo dentro del `api/` de `core/urls.py`). Dejarlo en `/api/token/` y actualizar las dos
  referencias del frontend (`auth.service.ts` y `auth.interceptor.ts`). Va aparte de A1 para no
  mezclar dos cambios distintos en la misma tarea.

### Bloque B — Recuperar lo que ya existe

- [x] **B1. Tienda (dónde se compró) en el frontend** · repo: `ambos` · depende de: —
  El API ya devuelve `store`; falta declararlo, elegirlo en el formulario y verlo en detalle y
  listados. Incluye la opción `Otro / No especificado`.
  ✅ **Completada el 29/09/2026** — doc: `retro-app/docs/history/2026-09-mejoras-inventario.md`
  (Backend sin tocar: el campo ya existía. Hecho junto con B2, que tocaba los mismos archivos.)
- [x] **B2. Funda (protective) en el frontend** · repo: `retro-app` · depende de: —
  El API ya devuelve `protective` (`Sin funda`, `Bolsa plástica`, `Funda PET`); falta lo mismo que B1.
  ✅ **Completada el 29/09/2026** (misma tarea que B1) — doc:
  `retro-app/docs/history/2026-09-mejoras-inventario.md`

### Bloque C — Mejoras de uso diario

- [x] **C1. Filtros que se mantienen al volver a la lista** · repo: `retro-app` · depende de: —
  Búsqueda, plataforma y orden se conservan al entrar en un artículo y volver.
  ✅ **Completada el 29/09/2026** — doc: `retro-app/docs/history/2026-09-mejoras-inventario.md`
  ⚠️ Se intentó primero con los filtros en la **URL** y **se descartó** (la lista no cargaba y se
  multiplicaban las peticiones; ver la nota del historial). La versión final guarda los filtros
  **en memoria**, sin tocar la URL, el buscador ni la paginación.
- [x] **C2. Botón "Borrar filtros"** · repo: `retro-app` · depende de: C1
  Limpia todos los filtros; solo aparece si hay alguno activo.
  ✅ **Completada el 29/09/2026** (misma tarea que C1) — doc:
  `retro-app/docs/history/2026-09-mejoras-inventario.md`

### Bloque D — Mejoras de valor

- [x] **D1. Precio del artículo + precio total** · repo: `ambos` · depende de: —
  `price` se queda como precio del artículo y se añade `total_price` (lo pagado con gastos). El
  usuario escribe los dos; si deja el total vacío se copia el artículo, y un total menor que el
  artículo se rechaza. **Sin desglose** de envío/comisión (decisión del humano).
  ✅ **Completada el 29/09/2026** — docs: `retro-api/docs/history/2026-09-mejoras-inventario.md` y
  `retro-app/docs/history/2026-09-mejoras-inventario.md`
  🔧 De paso se corrigió un fallo arrastrado de A1: `manage.py test` no ejecutaba la suite completa
  por un choque entre `inventory/tests.py` y `inventory/tests/`. Eliminado el archivo vacío.
- [x] **D2. Enlace de la compra + botón "Ver compra"** · repo: `ambos` · depende de: —
  Campo `purchase_url` (solo `http`/`https`) y botón en el detalle que abre la compra en pestaña
  nueva con `rel="noopener noreferrer"`.
  ✅ **Completada el 29/09/2026** — docs: `retro-api/docs/history/2026-09-mejoras-inventario.md` y
  `retro-app/docs/history/2026-09-mejoras-inventario.md`
  🔧 De paso se corrigió un fallo propio en el admin (`Accessory` con un campo `edition` que no
  existe) y se añadió `inventory/tests/test_admin_inventario.py` para que no vuelva a pasar.

### Bloque E — Base sólida

- [x] **E1. Preparar la infraestructura de tests** · repo: `ambos` · depende de: —
  Backend con pytest + pytest-django y frontend con Vitest: configuración y un test que pasa.
  ✅ **Hecho de facto dentro de A1**: paquete `inventory/tests/` con `__init__.py` y los primeros
  tests corriendo con el runner de Django. Queda decidir (tarea propia si se quiere) si se adopta
  `pytest` además del runner de Django, y montar la configuración de Vitest en el frontend.
  ✅ **Completada el 30/09/2026 (parte de frontend)** — `npm test` ya arranca: tenía un
  `src/app/app.spec.ts` heredado de la plantilla de Angular que importaba `./app` (el archivo real
  es `app.component.ts`) y **hacía fallar los tests antes de empezar**. Arreglado, y de paso se
  añadieron los primeros tests de verdad del frontend (20 en total): `core/auth.service.spec.ts`
  cubre la caducidad del token y la renovación compartida de E7. Doc:
  `retro-app/docs/history/2026-09-mejoras-inventario.md`
  ⏳ Sigue pendiente **decidir** si se adopta `pytest` además del runner de Django (tarea propia).
- [ ] **E2. Tests de permisos, validaciones y N+1** · repo: `retro-api` · depende de: E4
  (La parte de login ya está cubierta por A1, no se repite.) Permisos 401/403 en cada recurso,
  cada `validate_*` de los serializers y `assertNumQueries` en los listados.
- [ ] **E3. Revisar qué datos manda la API y el frontend no usa** · repo: `ambos` · depende de: —
  Buscar más casos como `store`/`protective` para no rehacer trabajo dos veces.
- [x] **E4. Permisos explícitos en los endpoints** · repo: `retro-api` · depende de: E1
  `IsAuthenticated` por defecto y `AllowAny` solo donde se justifique.
  ✅ **Completada el 29/09/2026** — antes, sin token, la API devolvía 200 (leer), 204 (borrar) y
  admitía subidas de imágenes; ahora responde 401. Doc: `retro-api/docs/history/2026-09-mejoras-inventario.md`
  🔍 Detectado además que `RegistroView` **no tiene ruta** (`/api/register/` da 404): es código
  muerto. Decidir si el registro debe existir sigue pendiente (§13.7 del `AGENTS.md`).
- [x] **E5. Validar `object_id` al subir imágenes** · repo: `retro-api` · depende de: E1
  ✅ **Completada el 29/09/2026** — antes se aceptaba cualquier `object_id` (creaba carpetas
  fantasma `unknown-999999`), un `content_type_model` inventado daba **500 con la traza**, y se
  podían colgar fotos de modelos que no deben llevarlas. Ahora: lista cerrada (consola/juego/
  accesorio) + el artículo tiene que existir → **400** y sin escribir nada en disco.
  Doc: `retro-api/docs/history/2026-09-mejoras-inventario.md`
  🔍 De paso se detectaron **2 imágenes rotas** en el accesorio "Demo Winter Releases '98"; el humano
  las borró y subió una nueva. Estado final: **0 referencias rotas**.
  Que no se puedan crear imágenes apuntando a artículos que no existen.
- [x] **E6. Freno de intentos en login y subidas (throttling)** · repo: `retro-api` · depende de: E1
  ✅ **Completada el 30/09/2026** — 10 intentos/min en login y refresh, 20/hora en subidas de
  imágenes. Antes no había ningún límite: 6 intentos de login seguidos se atendían todos.
  Doc: `retro-api/docs/history/2026-09-mejoras-inventario.md`
  📌 Deuda anotada: el login de la app dice "Credenciales inválidas" también cuando la API responde
  **429** por demasiados intentos (tarea corta de frontend, pendiente de aprobar).
- [x] **E7. Revisar el manejo de la sesión en el frontend** · repo: `retro-app` · depende de: A2
  Completada el 30/09/2026 · doc: `retro-app/docs/history/2026-09-mejoras-inventario.md`
  Guard del token caducado y evitar múltiples peticiones de refresco a la vez.
- [ ] **E8. Decidir y, si toca, implementar la paginación** · repo: `ambos` · depende de: —
  Solo si la colección va a crecer: hoy el navegador se descarga la lista completa.
- [ ] **E9. Pasar Prettier a todo el proyecto** · repo: `ambos` · depende de: —
  Hay archivos que no cumplen el formato del proyecto (líneas de más de 100 caracteres, código
  compactado en una sola línea). Se detectó durante B1: formatear solo los archivos tocados
  reformateaba más de 100 líneas por archivo y mezclaba dos cambios en el mismo commit. Se hace
  como tarea propia y en un commit **solo de formato**, sin cambios de comportamiento.

### Bloque F — Mantenimiento barato

- [ ] **F1. `.env.example` y limpieza de artefactos versionados** · repo: `retro-api` · depende de: —
  Plantilla sin secretos para montar el proyecto desde cero; decidir qué sale de Git.
- [ ] **F2. Actualizar la documentación (`README`, `HISTORIAL`, `AGENTS.md`)** · repo: `ambos` · depende de: —

## Fuera de alcance (decidido NO hacer)

- Comparador de precios con Wallapop/Vinted: sin API pública; el scraping va contra sus términos y
  se rompe con cada cambio de diseño.
- Conexión automática con las cuentas de las plataformas de compraventa.

## Ideas para más adelante (sin compromiso, no están en este plan)

Valor actual de la colección frente a lo pagado · registrar a quién se le ha prestado un artículo ·
exportar a CSV/Excel (seguro, inventario) · lista de deseos con precio objetivo.

## Riesgos y notas

- **D1 y D2 tocan base de datos** (migraciones nuevas). Se hacen al final de su bloque, con backup
  previo y revisando la migración a mano (`AGENTS.md` §12.3).
- **A1 puede tocar la autenticación de toda la app**: si se hace mal, nadie entra. Es la primera
  tarea y se verifica a mano antes de seguir.
- **E8 (paginación) cambia el contrato de la API** (de lista a objeto con `results`). Si se decide
  hacer, obliga a tocar las tres listas del frontend a la vez. Por eso está al final y es opcional.
- Cada tarea se documenta en `retro-api/docs/history/` y/o `retro-app/docs/history/` **solo** cuando
  la confirmes (§10.1 del `AGENTS.md`).
- Ninguna tarea se da por terminada sin su test (o el motivo por el que no aplica).

## Registro de avance

| Tarea | Estado | Confirmada el | Documento |
|---|---|---|---|
| A1 | ✅ **Completada** | 29/09/2026 | `retro-api/docs/history/2026-09-mejoras-inventario.md` |
| A2 | ✅ **Completada** | 29/09/2026 | `retro-app/docs/history/2026-09-mejoras-inventario.md` |
| A3 | ⏳ Pendiente | — | — |
| B1 | ✅ **Completada** | 29/09/2026 | `retro-app/docs/history/2026-09-mejoras-inventario.md` |
| B2 | ✅ **Completada** (con B1) | 29/09/2026 | `retro-app/docs/history/2026-09-mejoras-inventario.md` |
| C1 | ✅ **Completada** (versión en memoria; la de la URL se descartó) | 29/09/2026 | `retro-app/docs/history/2026-09-mejoras-inventario.md` |
| C2 | ✅ **Completada** (con C1) | 29/09/2026 | `retro-app/docs/history/2026-09-mejoras-inventario.md` |
| D1 | ✅ **Completada** (precio artículo + total; sin desglose) | 29/09/2026 | `retro-api/docs/history/2026-09-mejoras-inventario.md` · `retro-app/docs/history/2026-09-mejoras-inventario.md` |
| D2 | ✅ **Completada** (enlace de compra + botón "Ver compra") | 29/09/2026 | `retro-api/docs/history/2026-09-mejoras-inventario.md` · `retro-app/docs/history/2026-09-mejoras-inventario.md` |
| E1 | ✅ **Completada** (backend en A1; frontend el 30/09/2026: `npm test` arranca y 20 tests pasan) | 30/09/2026 | `retro-app/docs/history/2026-09-mejoras-inventario.md` |
| E2 | ⏳ Pendiente (bloque E: seguridad y calidad) | — | — |
| E3 | ⏳ Pendiente | — | — |
| E4 | ✅ **Completada** (API cerrada: sin token responde 401 en los 5 recursos) | 29/09/2026 | `retro-api/docs/history/2026-09-mejoras-inventario.md` |
| E5 | ✅ **Completada** (destino validado: lista cerrada + el artículo debe existir) | 29/09/2026 | `retro-api/docs/history/2026-09-mejoras-inventario.md` |
| E6 | ✅ **Completada** (10/min en login, 20/hora en subidas) | 30/09/2026 | `retro-api/docs/history/2026-09-mejoras-inventario.md` |
| E7 | ✅ **Completada** (guard con caducidad y renovación compartida) | 30/09/2026 | `retro-app/docs/history/2026-09-mejoras-inventario.md` |
| E8 | ⏳ Pendiente | — | — |
| E9 | ⏳ Pendiente | — | — |
| F1 | ⏳ Pendiente | — | — |
| F2 | ⏳ Pendiente | — | — |
