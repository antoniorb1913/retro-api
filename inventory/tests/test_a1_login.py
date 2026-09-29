"""
Tests de la tarea A1: autenticación con email (JWT).

Contexto: el frontend envía `email` + `password` al endpoint del token, pero el
`TokenObtainPairView` de SimpleJWT espera por defecto el campo `username`. Eso hacía
que el login devolviera 400 y la app no dejara entrar a ningún usuario normal.

La corrección está en `core/settings.py` (clave `USERNAME_FIELD` de `SIMPLE_JWT`).

Ejecutar solo estos tests:
    docker compose exec api python manage.py test inventory.tests.test_a1_login
"""
import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()

EMAIL = 'a1.login@example.com'
PASSWORD = 'ClaveDePrueba123!'


class LoginPorEmailTests(TestCase):
    """Comprueba que el login se hace con email y que rechaza credenciales inválidas."""

    @classmethod
    def setUpTestData(cls):
        User.objects.create_user(
            email=EMAIL,
            username='a1_login',
            password=PASSWORD,
        )

    def setUp(self):
        self.client = Client()

    def _login(self, email, password):
        """Pide un token JWT con las credenciales indicadas."""
        return self.client.post(
            '/api/api/token/',
            data=json.dumps({'email': email, 'password': password}),
            content_type='application/json',
        )

    def test_login_con_email_devuelve_tokens(self):
        """El login con email y contraseña correctos devuelve access y refresh."""
        respuesta = self._login(EMAIL, PASSWORD)

        self.assertEqual(respuesta.status_code, 200, 'El login debería devolver 200')

        cuerpo = respuesta.json()
        self.assertIn('access', cuerpo)
        self.assertIn('refresh', cuerpo)
        self.assertGreater(len(cuerpo['access']), 20, 'El access token está vacío')
        self.assertGreater(len(cuerpo['refresh']), 20, 'El refresh token está vacío')

    def test_el_token_abre_un_endpoint_protegido(self):
        """El token obtenido sirve para autenticarse en la API."""
        token = self._login(EMAIL, PASSWORD).json()['access']

        respuesta = self.client.get('/api/consoles/', HTTP_AUTHORIZATION=f'Bearer {token}')

        self.assertEqual(respuesta.status_code, 200)

    def test_email_inexistente_no_entra(self):
        """Un email que no existe no obtiene token."""
        respuesta = self._login('no.existe@example.com', PASSWORD)

        self.assertEqual(respuesta.status_code, 401)

    def test_contrasena_incorrecta_no_entra(self):
        """Una contraseña incorrecta no obtiene token."""
        respuesta = self._login(EMAIL, 'ClaveIncorrecta999!')

        self.assertEqual(respuesta.status_code, 401)
