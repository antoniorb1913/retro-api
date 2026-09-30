"""
Tests de la tarea E2: cobertura de los listados, de las validaciones y de los permisos.

Qué se comprueba aquí, y por qué:

  1. **Listados sin N+1.** Cada listado tiene que hacer **siempre el mismo número de consultas**,
     sin importar cuántos artículos haya. Se comprueba con 5 artículos y se vuelve a comprobar con
     15: si el número sube, alguien ha quitado un `prefetch_related` y el listado vuelve a hacer una
     consulta por artículo.
  2. **Validaciones de campo.** Valores fuera de las opciones permitidas, textos demasiado largos,
     números que no son números, fechas inválidas y archivos que no son imágenes: todo eso tiene que
     responder **400**, nunca 500 ni un guardado a medias.
  3. **Permisos.** Sin token, los cinco recursos responden **401** (la parte de lectura y escritura
     ya está en `test_e4_permisos.py`; aquí se añade que tampoco se entra con un token inventado).

**Sobre el 403 (decidido el 30/09/2026):** esta aplicación es de un solo dueño y **no hay ningún
permiso más fino que "estar autenticado"**: los cinco viewsets usan `IsAuthenticated` y no existe
propiedad por usuario ni roles. Por eso **no hay ningún caso que deba recibir 403** y no se prueba:
sería un test que pasa por no existir la comprobación, no por estar bien. El día que se añada un
permiso real (por ejemplo, que borrar exija `is_staff`), su 403 se prueba junto a ese cambio.

Ejecutar solo estos tests:
    docker compose exec api python manage.py test inventory.tests.test_e2_cobertura
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient

from inventory.models.Accessory import Accessory
from inventory.models.Console import Console
from inventory.models.Game import Game
from inventory.models.Image import ItemImage
from inventory.models.Missing_component import MissingComponent
from inventory.tests.test_e5_imagenes import png_valido

User = get_user_model()

# Los cinco recursos del inventario y cuántas consultas debe hacer cada listado, con cualquier
# número de artículos. Los tres primeros son 3 porque prefetchean componentes e imágenes.
CONSULTAS_POR_LISTADO = {
    'consoles': 3,
    'games': 3,
    'accessories': 3,
    'images': 1,
    'components': 1,
}

# Un artículo cualquiera, con todos los campos obligatorios mínimos.
ARTICULO = {'name': 'Artículo de prueba', 'status': 'GOOD', 'store': 'Wallapop', 'price': '10.00'}


class CoberturaTests(TestCase):
    """Listados, validaciones y permisos de los cinco recursos."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='e2.cobertura@example.com',
            username='e2_cobertura',
            password='ClaveDePrueba123!',
        )

        piezas = [MissingComponent.objects.create(name=f'Pieza E2 {i}') for i in range(2)]
        for modelo in (Console, Game, Accessory):
            tipo = ContentType.objects.get_for_model(modelo)
            for i in range(5):
                articulo = modelo.objects.create(
                    name=f'{modelo.__name__} E2 {i}',
                    status='GOOD',
                    store='Wallapop',
                    price=Decimal('10.00'),
                )
                articulo.missing_components.set(piezas)
                ItemImage.objects.create(content_type=tipo, object_id=articulo.id, image=f'e2/{i}.webp')

    def setUp(self):
        # La autenticación va aquí y no en `setUpTestData`: ese método se ejecuta **una sola vez**
        # para toda la clase, y Django crea una instancia nueva del test en cada método, así que lo
        # que se guarde en `cls` se pierde. Costó un rato descubrirlo (los tests salían todos 401).
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Un cliente aparte, sin sesión, para las pruebas de permisos.
        self.anonimo = APIClient()

    # ── 1. Listados sin N+1 ──────────────────────────────────────────────────

    def test_los_listados_no_crecen_en_consultas_con_5_articulos(self):
        """Cada listado hace un número fijo de consultas, no una por artículo."""
        for ruta, esperadas in CONSULTAS_POR_LISTADO.items():
            with self.subTest(listado=ruta):
                with self.assertNumQueries(esperadas):
                    self.client.get(f'/api/{ruta}/')

    def test_los_listados_siguen_igual_con_tres_veces_mas_articulos(self):
        """
        La prueba de verdad del N+1: con 15 artículos en vez de 5, el número de consultas tiene
        que ser exactamente el mismo. Si alguien quita un `prefetch_related`, esto falla.
        """
        for modelo in (Console, Game, Accessory):
            tipo = ContentType.objects.get_for_model(modelo)
            for i in range(10, 15):
                articulo = modelo.objects.create(
                    name=f'{modelo.__name__} E2 {i}',
                    status='GOOD',
                    store='Wallapop',
                    price=Decimal('10.00'),
                )
                articulo.missing_components.set(
                    MissingComponent.objects.filter(name__startswith='Pieza E2')
                )
                ItemImage.objects.create(content_type=tipo, object_id=articulo.id, image=f'e2/{i}.webp')

        for ruta, esperadas in CONSULTAS_POR_LISTADO.items():
            with self.subTest(listado=ruta):
                with self.assertNumQueries(esperadas):
                    self.client.get(f'/api/{ruta}/')

    def test_el_listado_devuelve_todos_los_articulos(self):
        """El listado no se deja artículos por el camino (ni de más ni de menos)."""
        # Imágenes: 5 por cada tipo de artículo (consola, juego y accesorio) = 15.
        # Componentes: solo las 2 piezas que se crean en `setUpTestData`.
        esperados_por_listado = {
            'consoles': 5,
            'games': 5,
            'accessories': 5,
            'images': 15,
            'components': 2,
        }
        for ruta, esperados in esperados_por_listado.items():
            with self.subTest(listado=ruta):
                respuesta = self.client.get(f'/api/{ruta}/')
                self.assertEqual(respuesta.status_code, 200)
                self.assertEqual(len(respuesta.json()), esperados)

    # ── 2. Validaciones: opciones permitidas ─────────────────────────────────

    def test_un_estado_inventado_responde_400(self):
        datos = {**ARTICULO, 'status': 'PERFECTO'}

        respuesta = self.client.post('/api/consoles/', datos, format='json')

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('status', respuesta.json())

    def test_una_tienda_inventada_responde_400(self):
        datos = {**ARTICULO, 'store': 'La tienda de mi barrio'}

        respuesta = self.client.post('/api/consoles/', datos, format='json')

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('store', respuesta.json())

    def test_una_plataforma_inventada_responde_400(self):
        datos = {**ARTICULO, 'platform': 'Super Nintendo 128'}

        respuesta = self.client.post('/api/consoles/', datos, format='json')

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('platform', respuesta.json())

    def test_una_funda_inventada_responde_400(self):
        datos = {**ARTICULO, 'protective': 'Caja fuerte'}

        respuesta = self.client.post('/api/consoles/', datos, format='json')

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('protective', respuesta.json())

    def test_los_valores_validos_se_aceptan(self):
        """El otro lado de la moneda: los valores reales tienen que entrar sin problema."""
        respuesta = self.client.post(
            '/api/games/',
            {**ARTICULO, 'name': 'Juego válido', 'status': 'MINT', 'store': 'Vinted', 'platform': 'PS2'},
            format='json',
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()['status'], 'MINT')

    # ── 3. Validaciones: longitudes y campos obligatorios ────────────────────

    def test_no_se_puede_crear_un_articulo_sin_nombre(self):
        respuesta = self.client.post('/api/consoles/', {'status': 'GOOD', 'store': 'Wallapop'}, format='json')

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('name', respuesta.json())

    def test_un_nombre_de_200_caracteres_se_acepta(self):
        """El límite del campo son 200: justo en el borde tiene que entrar."""
        respuesta = self.client.post(
            '/api/consoles/',
            {**ARTICULO, 'name': 'A' * 200},
            format='json',
        )

        self.assertEqual(respuesta.status_code, 201)

    def test_un_nombre_de_201_caracteres_responde_400(self):
        respuesta = self.client.post(
            '/api/consoles/',
            {**ARTICULO, 'name': 'A' * 201},
            format='json',
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('name', respuesta.json())

    def test_un_modelo_demas_largo_del_permitido_responde_400(self):
        respuesta = self.client.post(
            '/api/consoles/',
            {**ARTICULO, 'model': 'M' * 51},
            format='json',
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('model', respuesta.json())

    # ── 4. Validaciones: números y fechas ────────────────────────────────────

    def test_un_precio_que_no_es_un_numero_responde_400(self):
        respuesta = self.client.post(
            '/api/consoles/',
            {**ARTICULO, 'price': 'me costó caro'},
            format='json',
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('price', respuesta.json())

    def test_un_precio_negativo_se_acepta_hoy(self):
        """
        ⚠️ **Esto documenta un fallo, no una buena costumbre.**

        `price` es un `DecimalField` sin `MinValueValidator` (`inventory/models/Base.py`), así que
        la API acepta un precio negativo y lo guarda. Debería responder **400**: un precio no puede
        ser negativo, y además `total_price` se copia de `price`, así que un negativo descuadra las
        sumas del frontend (el "Total invertido" las resta en vez de sumarlas).

        Este test fija el comportamiento actual para que el fallo quede por escrito y no se olvide.
        **Cuando se decida arreglarlo** (añadir `MinValueValidator(0)` al campo), hay que cambiar la
        comprobación de 201 a 400 en lugar de borrar este test.
        """
        respuesta = self.client.post(
            '/api/consoles/',
            {**ARTICULO, 'name': 'Consola con precio negativo', 'price': '-15.00'},
            format='json',
        )

        self.assertEqual(respuesta.status_code, 201, 'si esto falla, ¡bien! alguien ya lo arregló')
        self.assertEqual(respuesta.json()['price'], '-15.00')
        self.assertEqual(respuesta.json()['total_price'], '-15.00')

    def test_una_fecha_de_compra_invalida_responde_400(self):
        respuesta = self.client.post(
            '/api/consoles/',
            {**ARTICULO, 'acquisition_date': '32/13/2026'},
            format='json',
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('acquisition_date', respuesta.json())

    def test_una_fecha_de_compra_valida_se_acepta(self):
        respuesta = self.client.post(
            '/api/consoles/',
            {**ARTICULO, 'acquisition_date': '2026-09-30'},
            format='json',
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()['acquisition_date'], '2026-09-30')

    # ── 5. Validaciones: la imagen tiene que ser una imagen ──────────────────

    def test_subir_un_archivo_que_no_es_una_imagen_responde_400(self):
        """
        El destino es válido, pero el archivo no es una imagen. Tiene que responder 400 y no
        guardar nada: si no, el backend se rompería al intentar convertirlo a WebP.
        """
        consola = Console.objects.first()
        archivo = SimpleUploadedFile('notas.txt', b'esto no es una imagen', content_type='text/plain')

        respuesta = self.client.post(
            '/api/images/',
            {'image': archivo, 'content_type_model': 'console', 'object_id': consola.id},
            format='multipart',
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertIn('image', respuesta.json())

    def test_una_imagen_de_verdad_si_se_sube(self):
        """El otro lado: un PNG real entra sin problema (así el test de arriba no engaña)."""
        consola = Console.objects.first()

        respuesta = self.client.post(
            '/api/images/',
            {
                'image': SimpleUploadedFile('foto.png', png_valido(), content_type='image/png'),
                'content_type_model': 'console',
                'object_id': consola.id,
            },
            format='multipart',
        )

        self.assertEqual(respuesta.status_code, 201)

    # ── 6. Permisos: sin token no se entra (el 403 no aplica, ver cabecera) ──

    def test_sin_token_los_cinco_listados_responden_401(self):
        for ruta in CONSULTAS_POR_LISTADO:
            with self.subTest(listado=ruta):
                self.assertEqual(self.anonimo.get(f'/api/{ruta}/').status_code, 401)

    def test_un_token_inventado_no_abre_ningun_listado(self):
        self.anonimo.credentials(HTTP_AUTHORIZATION='Bearer esto.no.es.un.token')

        for ruta in CONSULTAS_POR_LISTADO:
            with self.subTest(listado=ruta):
                self.assertEqual(self.anonimo.get(f'/api/{ruta}/').status_code, 401)
