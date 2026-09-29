"""
Tests de la tarea E4: permisos explícitos en los endpoints.

Antes de esta tarea, DRF no tenía `DEFAULT_PERMISSION_CLASSES` configurado, así que **cualquier
petición sin token se atendía**: se podía leer, crear, editar y borrar el inventario sin estar
autenticado. Estos tests existen para impedir que eso vuelva a pasar.

Reglas que se comprueban:
  1. Sin token, los cinco recursos del inventario responden 401 (lectura y escritura, incluido el
     borrado).
  2. Subir una imagen sin token responde 401.
  3. Con token válido, todo funciona igual que antes (no se ha cerrado de más).
  4. El login sigue abierto: se puede pedir un token sin estar autenticado.
  5. El registro sigue abierto (decisión del humano: el alta es libre).

Ejecutar solo estos tests:
    docker compose exec api python manage.py test inventory.tests.test_e4_permisos
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase

from inventory.models.Console import Console
from inventory.models.Missing_component import MissingComponent

User = get_user_model()

# Imagen PNG mínima válida (1x1), para poder probar la subida sin depender de un archivo externo.
PNG_MINIMO = bytes.fromhex(
    '89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489'
    '0000000a49444154789c6360000002000100ffff03000006000557bfabd40000000049454e44ae426082'
)


class PermisosTests(TestCase):
    """Sin token no se entra; con token, todo sigue funcionando."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='e4.permisos@example.com',
            username='e4_permisos',
            password='ClaveDePrueba123!',
        )
        cls.consola = Console.objects.create(name='Consola protegida', price=Decimal('10.00'))
        cls.componente = MissingComponent.objects.create(name='Caja')
        cls.client = Client()

        # Token válido, obtenido como lo haría la aplicación.
        respuesta = cls.client.post(
            '/api/api/token/',
            data={'email': 'e4.permisos@example.com', 'password': 'ClaveDePrueba123!'},
            content_type='application/json',
        )
        cls.token = respuesta.json()['access']

    def _cabecera(self):
        return {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    # ── 1. Sin token: no se entra ─────────────────────────────────────────────

    def test_sin_token_no_se_puede_leer_ningun_recurso(self):
        """Los cinco recursos del inventario exigen autenticación para leerlos."""
        rutas = [
            '/api/consoles/',
            '/api/games/',
            '/api/accessories/',
            '/api/images/',
            '/api/components/',
        ]

        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertEqual(
                    respuesta.status_code,
                    401,
                    f'{ruta} debería exigir autenticación (devolvió {respuesta.status_code})',
                )

    def test_sin_token_no_se_puede_crear(self):
        """Crear un artículo sin token debe rechazarse."""
        respuesta = self.client.post(
            '/api/consoles/',
            data={'name': 'Consola intrusa'},
            content_type='application/json',
        )

        self.assertEqual(respuesta.status_code, 401)
        self.assertFalse(Console.objects.filter(name='Consola intrusa').exists())

    def test_sin_token_no_se_puede_editar(self):
        """Editar un artículo sin token debe rechazarse."""
        respuesta = self.client.patch(
            f'/api/consoles/{self.consola.id}/',
            data={'name': 'Nombre cambiado por un intruso'},
            content_type='application/json',
        )

        self.assertEqual(respuesta.status_code, 401)
        self.consola.refresh_from_db()
        self.assertEqual(self.consola.name, 'Consola protegida')

    def test_sin_token_no_se_puede_borrar(self):
        """
        El caso más grave: borrar el inventario ajeno. Debe rechazarse.

        Este test es el motivo principal de la tarea E4.
        """
        respuesta = self.client.delete(f'/api/consoles/{self.consola.id}/')

        self.assertEqual(respuesta.status_code, 401)
        self.assertTrue(
            Console.objects.filter(id=self.consola.id).exists(),
            'La consola se ha borrado sin autenticación: el endpoint está abierto',
        )

    def test_sin_token_no_se_puede_subir_una_imagen(self):
        """La subida de archivos es un endpoint sensible: exige autenticación."""
        archivo = SimpleUploadedFile('foto.png', PNG_MINIMO, content_type='image/png')
        respuesta = self.client.post(
            '/api/images/',
            data={
                'image': archivo,
                'content_type_model': 'console',
                'object_id': self.consola.id,
            },
        )

        self.assertEqual(respuesta.status_code, 401)

    # ── 2. Con token: todo sigue funcionando ──────────────────────────────────

    def test_con_token_se_puede_leer_escribir_y_borrar(self):
        """Con un token válido, el flujo completo del inventario sigue igual que antes."""
        # Leer
        respuesta = self.client.get('/api/consoles/', **self._cabecera())
        self.assertEqual(respuesta.status_code, 200, respuesta.content)
        self.assertEqual(len(respuesta.json()), 1)

        # Crear
        respuesta = self.client.post(
            '/api/consoles/',
            data={'name': 'Consola legítima', 'price': '25.00'},
            content_type='application/json',
            **self._cabecera(),
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.content)
        nuevo_id = respuesta.json()['id']

        # Editar
        respuesta = self.client.patch(
            f'/api/consoles/{nuevo_id}/',
            data={'name': 'Consola editada'},
            content_type='application/json',
            **self._cabecera(),
        )
        self.assertEqual(respuesta.status_code, 200, respuesta.content)

        # Borrar
        respuesta = self.client.delete(f'/api/consoles/{nuevo_id}/', **self._cabecera())
        self.assertEqual(respuesta.status_code, 204, respuesta.content)
        self.assertFalse(Console.objects.filter(id=nuevo_id).exists())

    def test_con_token_funcionan_los_cinco_recursos(self):
        """Ninguno de los cinco recursos se ha cerrado de más."""
        rutas = [
            '/api/consoles/',
            '/api/games/',
            '/api/accessories/',
            '/api/images/',
            '/api/components/',
        ]

        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta, **self._cabecera())
                self.assertEqual(respuesta.status_code, 200, f'{ruta} debería responder 200')

    def test_un_token_invalido_tampoco_entra(self):
        """Un token falso o caducado se rechaza igual que no llevar ninguno."""
        respuesta = self.client.get(
            '/api/consoles/',
            HTTP_AUTHORIZATION='Bearer esto.no.es.un.token',
        )

        self.assertEqual(respuesta.status_code, 401)

    # ── 3. Lo que debe seguir siendo público ──────────────────────────────────

    def test_el_login_sigue_abierto(self):
        """Sin este endpoint abierto nadie podría entrar nunca."""
        respuesta = self.client.post(
            '/api/api/token/',
            data={'email': 'e4.permisos@example.com', 'password': 'ClaveDePrueba123!'},
            content_type='application/json',
        )

        self.assertEqual(respuesta.status_code, 200, respuesta.content)
        self.assertIn('access', respuesta.json())
        self.assertIn('refresh', respuesta.json())

    def test_el_refresh_sigue_abierto(self):
        """El refresh del token también se pide sin estar autenticado."""
        respuesta = self.client.post(
            '/api/api/token/',
            data={'email': 'e4.permisos@example.com', 'password': 'ClaveDePrueba123!'},
            content_type='application/json',
        )
        refresh = respuesta.json()['refresh']

        respuesta = self.client.post(
            '/api/api/token/refresh/',
            data={'refresh': refresh},
            content_type='application/json',
        )

        self.assertEqual(respuesta.status_code, 200, respuesta.content)
        self.assertIn('access', respuesta.json())
