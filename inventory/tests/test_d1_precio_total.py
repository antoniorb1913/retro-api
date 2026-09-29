"""
Tests de la tarea D1: precio del artículo (`price`) y precio total (`total_price`).

Reglas que se comprueban:
  1. Si solo se envía el precio del artículo, el total se copia automáticamente.
  2. Si se envían los dos, se guardan los dos.
  3. Un total menor que el precio del artículo se rechaza (no tiene sentido: el total
     incluye el artículo más gastos).
  4. Los artículos anteriores al campo (creados sin total) siguen funcionando.
  5. La API devuelve los dos campos y permite ordenar por el total.

Ejecutar solo estos tests:
    docker compose exec api python manage.py test inventory.tests.test_d1_precio_total
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from inventory.models.Console import Console

User = get_user_model()


class PrecioTotalTests(TestCase):
    """Reglas del campo `total_price` en la API del inventario."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='d1.precio@example.com',
            username='d1_precio',
            password='ClaveDePrueba123!',
        )
        cls.client = Client()
        respuesta = cls.client.post(
            '/api/api/token/',
            data={'email': 'd1.precio@example.com', 'password': 'ClaveDePrueba123!'},
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

    def test_sin_total_se_copia_el_precio(self):
        """Si no se envía total, se copia el precio del artículo."""
        respuesta = self._post('/api/consoles/', {'name': 'Consola sin gastos', 'price': '30.00'})

        self.assertEqual(respuesta.status_code, 201, respuesta.content)
        self.assertEqual(Decimal(respuesta.json()['price']), Decimal('30.00'))
        self.assertEqual(Decimal(respuesta.json()['total_price']), Decimal('30.00'))

    def test_total_mayor_que_el_precio_se_guarda(self):
        """Si hay gastos, el total se guarda tal cual."""
        respuesta = self._post(
            '/api/games/',
            {'name': 'Juego con envío', 'price': '30.00', 'total_price': '37.00'},
        )

        self.assertEqual(respuesta.status_code, 201, respuesta.content)
        self.assertEqual(Decimal(respuesta.json()['price']), Decimal('30.00'))
        self.assertEqual(Decimal(respuesta.json()['total_price']), Decimal('37.00'))

    def test_total_menor_que_el_precio_se_rechaza(self):
        """Un total menor que el precio del artículo es un error de datos."""
        respuesta = self._post(
            '/api/consoles/',
            {'name': 'Consola mal', 'price': '30.00', 'total_price': '20.00'},
        )

        self.assertEqual(respuesta.status_code, 400, respuesta.content)
        self.assertIn('total_price', respuesta.json())

    def test_total_igual_al_precio_se_acepta(self):
        """Poner el mismo valor en los dos campos es válido."""
        respuesta = self._post(
            '/api/accessories/',
            {'name': 'Mando igual', 'price': '25.00', 'total_price': '25.00'},
        )

        self.assertEqual(respuesta.status_code, 201, respuesta.content)

    def test_articulo_antiguo_sin_total_sigue_funcionando(self):
        """Un artículo creado antes del campo (total vacío) se lee sin errores."""
        viejo = Console.objects.create(name='Consola antigua', price=Decimal('40.00'))
        self.assertIsNone(viejo.total_price)

        respuesta = self.client.get(
            f'/api/consoles/{viejo.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Decimal(respuesta.json()['price']), Decimal('40.00'))

    def test_se_puede_ordenar_por_total(self):
        """La API acepta ordenar por `total_price`."""
        Console.objects.create(name='Barata', price=Decimal('10.00'), total_price=Decimal('10.00'))
        Console.objects.create(name='Cara', price=Decimal('10.00'), total_price=Decimal('99.00'))

        respuesta = self.client.get(
            '/api/consoles/?ordering=-total_price',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )

        self.assertEqual(respuesta.status_code, 200)
        nombres = [c['name'] for c in respuesta.json()]
        self.assertEqual(nombres[0], 'Cara', 'El total más alto debe ir primero')
