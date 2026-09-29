"""
Tests de la tarea E6: freno de intentos (throttling).

Antes de esta tarea **no había ningún límite**: se podían probar contraseñas a miles por minuto
con un programa. Eso es una puerta abierta a adivinar la contraseña por fuerza bruta.

Reglas que se comprueban:
  1. Pasarse de intentos en el login devuelve **429** (Too Many Requests).
  2. Dentro del límite, todo funciona igual (no se frena de más).
  3. La cuenta del dueño (`is_staff`) **no** se bloquea: sería bloquearse a sí mismo.
  4. Un usuario normal **sí** se bloquea (la exención es solo para staff).
  5. Subir imágenes tiene su propio límite, independiente del de login.

Tres notas técnicas que costaron un fallo real al escribir estos tests:

  - **Los límites NO se pueden cambiar con `override_settings`.** DRF los lee **una sola vez**, al
    cargar su módulo (`SimpleRateThrottle.THROTTLE_RATES` es un atributo de clase). Al intentarlo,
    el test parecía comprobar un límite de 3/min cuando en realidad se aplicaba el de producción,
    y el resultado era un "no frena" que no significaba nada. Por eso estos tests usan los límites
    **reales** de `core/settings.py`, que además es lo que de verdad queremos verificar.
  - **Los contadores viven en la caché y no se borran entre tests.** Sin limpiarla al empezar cada
    uno, un test contamina a los siguientes y aparecen fallos fantasma.
  - **`override_settings(CACHES=…)` no basta** para aislar el freno: `django.core.cache.cache`
    apunta a la caché real. Lo que aísla de verdad es limpiarla en `setUp`.

Ejecutar solo estos tests:
    docker compose exec api python manage.py test inventory.tests.test_e6_throttling
"""
import tempfile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from rest_framework.throttling import ScopedRateThrottle

from inventory.models.Console import Console
from inventory.tests.test_e5_imagenes import png_valido

User = get_user_model()


def limite_de(scope):
    """
    Devuelve cuántos intentos admite un ámbito (`login`, `refresh`, `subida`) antes de frenar.

    Se lee del freno real (`ScopedRateThrottle.THROTTLE_RATES`, que es donde DRF guarda los límites
    configurados en `settings.py`), así que si algún día se ajustan los números, los tests siguen
    valiendo sin tocarlos.
    """
    return ScopedRateThrottle().parse_rate(ScopedRateThrottle.THROTTLE_RATES[scope])[0]


class ThrottlingTests(TestCase):
    """El login y la subida de imágenes tienen freno de intentos."""

    @classmethod
    def setUpTestData(cls):
        cls.dueno = User.objects.create_user(
            email='dueno@example.com',
            username='dueno',
            password='ClaveDePrueba123!',
            is_staff=True,
        )
        cls.normal = User.objects.create_user(
            email='normal@example.com',
            username='normal',
            password='ClaveDePrueba123!',
        )
        cls.consola = Console.objects.create(name='Consola E6')

    def setUp(self):
        # El freno cuenta en la caché y no se limpia solo entre tests.
        cache.clear()
        self.client = Client()
        self.limite_login = limite_de('login')

    def _intento_login(self, email='falso@example.com', password='contrasena-mala'):
        return self.client.post(
            '/api/api/token/',
            data={'email': email, 'password': password},
            content_type='application/json',
        )

    def _subir_imagen(self, token):
        return self.client.post(
            '/api/images/',
            data={
                'image': SimpleUploadedFile('foto.png', png_valido(), content_type='image/png'),
                'content_type_model': 'console',
                'object_id': self.consola.id,
            },
            HTTP_AUTHORIZATION=f'Bearer {token}',
        )

    def _token_valido(self, email='normal@example.com', password='ClaveDePrueba123!'):
        return self._intento_login(email, password).json().get('access', '')

    # ── El login, frenado ─────────────────────────────────────────────────────

    def test_pasarse_de_intentos_en_el_login_devuelve_429(self):
        """
        El caso central de E6: sin límite se pueden probar contraseñas sin fin.

        Los primeros intentos se atienden (401 = credenciales malas). Al pasarse del límite, la API
        tiene que responder 429 en vez de seguir aceptando intentos.
        """
        codigos = [self._intento_login().status_code for _ in range(self.limite_login + 1)]

        self.assertEqual(
            codigos[-1],
            429,
            f'al pasar de {self.limite_login} intentos debería frenar. Códigos: {codigos}',
        )
        self.assertEqual(codigos[0], 401, 'los intentos dentro del límite se atienden con normalidad')

    def test_no_frena_antes_de_pasarse(self):
        """Justo en el límite todavía no frena: no se frena de más."""
        codigos = [self._intento_login().status_code for _ in range(self.limite_login)]

        self.assertNotIn(429, codigos, f'no debería frenar dentro del límite. Códigos: {codigos}')

    def test_el_freno_es_temporal_no_un_bloqueo(self):
        """
        Al acabarse el tiempo, se puede volver a intentar. Un bloqueo permanente dejaría al usuario
        fuera de su propia aplicación para siempre.
        """
        for _ in range(self.limite_login + 1):
            self._intento_login()
        self.assertEqual(self._intento_login().status_code, 429, 'debería estar frenado')

        # Se vacía la caché como si hubiera pasado el minuto.
        cache.clear()

        self.assertNotEqual(
            self._intento_login().status_code,
            429,
            'pasado el tiempo, el usuario tiene que poder volver a intentarlo',
        )

    def test_un_usuario_normal_se_bloquea(self):
        """A un usuario normal se le frena igual: el límite protege su contraseña."""
        codigos = [
            self._intento_login('normal@example.com', 'ClaveDePrueba123!').status_code
            for _ in range(self.limite_login + 1)
        ]

        self.assertIn(429, codigos, f'un usuario normal debería frenarse. Códigos: {codigos}')

    def test_entrar_dentro_del_limite_funciona(self):
        """Entrar normalmente (1 intento) no se ve afectado por el freno."""
        respuesta = self._intento_login('normal@example.com', 'ClaveDePrueba123!')

        self.assertEqual(respuesta.status_code, 200, respuesta.content)
        self.assertIn('access', respuesta.json())
        self.assertIn('refresh', respuesta.json())

    def test_el_refresh_tiene_su_propio_limite(self):
        """Refrescar el token también se limita, y es independiente del login."""
        refresh = self._intento_login('normal@example.com', 'ClaveDePrueba123!').json()['refresh']
        limite_refresh = limite_de('refresh')

        codigos = []
        for _ in range(limite_refresh + 1):
            respuesta = self.client.post(
                '/api/api/token/refresh/',
                data={'refresh': refresh},
                content_type='application/json',
            )
            codigos.append(respuesta.status_code)

        self.assertEqual(codigos[-1], 429, f'el refresh debería frenarse. Códigos: {codigos}')

        # Y ese freno no ha gastado el del login, que es otro contador.
        self.assertNotEqual(
            self._intento_login('normal@example.com', 'ClaveDePrueba123!').status_code,
            429,
            'el límite del refresh no debe afectar al del login',
        )

    # ── La exención del dueño ─────────────────────────────────────────────────

    def test_el_login_tambien_frena_al_dueno(self):
        """
        El login frena a todo el mundo, **incluido el dueño**, y es correcto que sea así.

        Cuando alguien pide un token todavía no ha demostrado quién es: DRF ve un usuario anónimo
        (`request.user` es `AnonymousUser`), así que el límite se cuenta por IP y la exención para
        `is_staff` no puede aplicarse. Con 10 intentos por minuto que se recuperan solos, al dueño
        no le molesta en la práctica.

        Este test deja escrito ese comportamiento para que a nadie le extrañe en el futuro (ni se
        "arregle" creyendo que es un fallo).
        """
        codigos = [
            self._intento_login('dueno@example.com', 'ClaveDePrueba123!').status_code
            for _ in range(self.limite_login + 1)
        ]

        self.assertEqual(codigos[0], 200, 'dentro del límite, el dueño entra con normalidad')
        self.assertEqual(
            codigos[-1],
            429,
            f'el login frena por IP aunque sea el dueño. Códigos: {codigos}',
        )

    # ── La subida de imágenes, con su propio límite ────────────────────────────

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix='test_e6_media_'))
    def test_la_subida_de_imagenes_tiene_su_propio_limite(self):
        """Subir archivos también se limita: es un endpoint pesado (convierte a WebP y escribe)."""
        token = self._token_valido()
        limite_subida = limite_de('subida')

        codigos = [self._subir_imagen(token).status_code for _ in range(limite_subida + 1)]

        self.assertEqual(codigos[0], 201, 'la primera subida debería funcionar')
        self.assertEqual(
            codigos[-1],
            429,
            f'al pasar de {limite_subida} subidas debería frenar. Códigos: {codigos}',
        )

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix='test_e6_media_'))
    def test_el_dueno_no_se_frena_al_subir_imagenes(self):
        """
        Aquí la exención **sí** funciona: la petición de subida ya lleva el token, así que DRF sabe
        quién es y ve que es el dueño (`is_staff`).

        Es el caso que de verdad importa: no bloquearse a sí mismo mientras cataloga.
        """
        # El dueño entra (1 intento, dentro del límite) y sube más fotos de las permitidas.
        token = self._intento_login('dueno@example.com', 'ClaveDePrueba123!').json()['access']
        limite_subida = limite_de('subida')

        codigos = [self._subir_imagen(token).status_code for _ in range(limite_subida + 2)]

        self.assertNotIn(
            429,
            codigos,
            f'el dueño no debería frenarse al subir. Códigos: {codigos}',
        )

    @override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix='test_e6_media_'))
    def test_subir_imagenes_no_gasta_el_limite_del_login(self):
        """Cada límite es independiente: subir fotos no te deja sin poder entrar."""
        token = self._token_valido()
        for _ in range(2):
            self._subir_imagen(token)

        respuesta = self._intento_login('normal@example.com', 'ClaveDePrueba123!')

        self.assertEqual(
            respuesta.status_code,
            200,
            'subir fotos no debería gastar el límite del login',
        )
