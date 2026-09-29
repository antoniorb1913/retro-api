"""
Tests de la tarea D2: enlace de compra (`purchase_url`).

Reglas que se comprueban:
  1. Un enlace web normal se guarda y se devuelve.
  2. El campo es opcional: se puede dejar vacío.
  3. Solo se aceptan `http` y `https`: cualquier otro esquema se rechaza.
  4. Se rechaza algo que no es una URL.
  5. El campo aparece en los listados y se puede editar.

Ejecutar solo estos tests:
    docker compose exec api python manage.py test inventory.tests.test_d2_enlace_compra
"""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from inventory.models.Console import Console

User = get_user_model()


class EnlaceCompraTests(TestCase):
    """Reglas del campo `purchase_url` en la API del inventario."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='d2.enlace@example.com',
            username='d2_enlace',
            password='ClaveDePrueba123!',
        )
        cls.client = Client()
        respuesta = cls.client.post(
            '/api/api/token/',
            data={'email': 'd2.enlace@example.com', 'password': 'ClaveDePrueba123!'},
            content_type='application/json',
        )
        cls.token = respuesta.json()['access']

    def _post(self, endpoint, datos):
        return self.client.post(
            endpoint,
            data=datos,
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )

    def test_guarda_un_enlace_valido(self):
        """Un enlace normal se guarda y se devuelve tal cual."""
        url = 'https://www.wallapop.com/item/game-boy-123456'
        respuesta = self._post('/api/consoles/', {'name': 'Consola con enlace', 'purchase_url': url})

        self.assertEqual(respuesta.status_code, 201, respuesta.content)
        self.assertEqual(respuesta.json()['purchase_url'], url)

    def test_el_enlace_es_opcional(self):
        """Se puede crear un artículo sin enlace."""
        respuesta = self._post('/api/consoles/', {'name': 'Consola sin enlace'})

        self.assertEqual(respuesta.status_code, 201, respuesta.content)
        self.assertIsNone(respuesta.json()['purchase_url'])

    def test_acepta_http_y_https(self):
        """Los dos esquemas web válidos se aceptan."""
        for url in ('http://ejemplo.com/anuncio', 'https://ejemplo.com/anuncio'):
            with self.subTest(url=url):
                respuesta = self._post('/api/consoles/', {'name': f'Consola {url}', 'purchase_url': url})
                self.assertEqual(respuesta.status_code, 201, respuesta.content)

    def test_rechaza_esquemas_peligrosos(self):
        """
        Un enlace `javascript:` se pinta en el frontend: aceptarlo sería un vector de ataque.
        Debe rechazarse igual que cualquier otro esquema que no sea http/https.
        """
        peligrosos = [
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            'file:///etc/passwd',
        ]

        for url in peligrosos:
            with self.subTest(url=url):
                respuesta = self._post('/api/consoles/', {'name': f'Consola {url}', 'purchase_url': url})
                self.assertEqual(respuesta.status_code, 400, f'{url} debería rechazarse')
                self.assertIn('purchase_url', respuesta.json())

    def test_rechaza_lo_que_no_es_una_url(self):
        """Texto suelto tampoco vale."""
        respuesta = self._post('/api/consoles/', {'name': 'Consola texto', 'purchase_url': 'lo compre en la tienda'})

        self.assertEqual(respuesta.status_code, 400, respuesta.content)
        self.assertIn('purchase_url', respuesta.json())

    def test_rechaza_un_enlace_demasiado_largo(self):
        """El campo admite 500 caracteres; por encima se rechaza con un 400 claro, no con un error de base de datos."""
        respuesta = self._post(
            '/api/consoles/',
            {'name': 'Consola enlace largo', 'purchase_url': 'https://ejemplo.com/' + 'a' * 520},
        )

        self.assertEqual(respuesta.status_code, 400, respuesta.content)
        self.assertIn('purchase_url', respuesta.json())

    def test_el_enlace_se_puede_editar_y_vaciar(self):
        """Se puede cambiar el enlace y también borrarlo."""
        consola = Console.objects.create(name='Consola editable', purchase_url='https://ejemplo.com/a')

        respuesta = self.client.patch(
            f'/api/consoles/{consola.id}/',
            data={'purchase_url': 'https://ejemplo.com/b'},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(respuesta.status_code, 200, respuesta.content)
        self.assertEqual(respuesta.json()['purchase_url'], 'https://ejemplo.com/b')

        respuesta = self.client.patch(
            f'/api/consoles/{consola.id}/',
            data={'purchase_url': None},
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )
        self.assertEqual(respuesta.status_code, 200, respuesta.content)
        self.assertIsNone(respuesta.json()['purchase_url'])

    def test_aparece_en_el_listado(self):
        """El listado devuelve el campo (el frontend lo necesita para pintar el botón)."""
        Console.objects.create(name='Consola listada', purchase_url='https://ejemplo.com/c')

        respuesta = self.client.get('/api/consoles/', HTTP_AUTHORIZATION=f'Bearer {self.token}')

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn('purchase_url', respuesta.json()[0])
