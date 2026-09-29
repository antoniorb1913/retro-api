"""
Tests de la tarea E5: validación al subir imágenes.

Antes de esta tarea, `ImageUploadSerializer` (el que se usa para subir) **no validaba nada**:
  1. Aceptaba cualquier `object_id`, aunque no existiera ningún artículo con ese id. Se creaba la
     imagen y una carpeta huérfana en el disco (`media/consoles/unknown-999999/...`).
  2. Un `content_type_model` que no existiera **no** daba un error controlado: reventaba con
     `DoesNotExist` y Django devolvía una **página 500 con la traza completa**.
  3. Se podía decir que la imagen pertenece a cualquier modelo de la app `inventory`, incluidos los
     que no deberían llevar fotos (por ejemplo `missingcomponent`, que es el catálogo de piezas).

Reglas que se comprueban ahora:
  - Solo se admiten `console`, `game` y `accessory` como destino.
  - El artículo destino tiene que existir de verdad.
  - Una subida correcta sigue funcionando y guarda el archivo.
  - Un rechazo **no deja basura** en el disco.

Ejecutar solo estos tests:
    docker compose exec api python manage.py test inventory.tests.test_e5_imagenes
"""
import os
import shutil
import struct
import tempfile
import zlib
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from inventory.models.Accessory import Accessory
from inventory.models.Console import Console
from inventory.models.Image import ItemImage
from inventory.models.Missing_component import MissingComponent

User = get_user_model()


def png_valido(ancho=8, alto=8):
    """Genera un PNG real y mínimo, para que el campo `image` lo acepte."""
    def bloque(tipo, datos):
        return (
            struct.pack('>I', len(datos))
            + tipo
            + datos
            + struct.pack('>I', zlib.crc32(tipo + datos) & 0xFFFFFFFF)
        )

    filas = b''.join(b'\x00' + b'\xff\x00\xff' * ancho for _ in range(alto))
    return (
        b'\x89PNG\r\n\x1a\n'
        + bloque(b'IHDR', struct.pack('>IIBBBBB', ancho, alto, 8, 2, 0, 0, 0))
        + bloque(b'IDAT', zlib.compress(filas))
        + bloque(b'IEND', b'')
    )


# Las imágenes se guardan en una carpeta temporal para no tocar `media/` durante los tests.
@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix='test_e5_media_'))
class ValidacionImagenesTests(TestCase):
    """El endpoint de imágenes rechaza destinos inválidos sin dejar basura."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='e5.imagenes@example.com',
            username='e5_imagenes',
            password='ClaveDePrueba123!',
        )
        cls.consola = Console.objects.create(name='Consola con foto', price=Decimal('10.00'))
        cls.accesorio = Accessory.objects.create(name='Accesorio con foto')
        cls.componente = MissingComponent.objects.create(name='Caja')

        cls.client = Client()
        respuesta = cls.client.post(
            '/api/api/token/',
            data={'email': 'e5.imagenes@example.com', 'password': 'ClaveDePrueba123!'},
            content_type='application/json',
        )
        cls.token = respuesta.json()['access']

    @classmethod
    def tearDownClass(cls):
        # Limpieza de la carpeta temporal de media
        from django.conf import settings
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def _subir(self, **campos):
        datos = {
            'image': SimpleUploadedFile('foto.png', png_valido(), content_type='image/png'),
            'content_type_model': 'console',
            'object_id': self.consola.id,
        }
        datos.update(campos)
        return self.client.post(
            '/api/images/',
            data=datos,
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )

    def _archivos_en_disco(self):
        from django.conf import settings
        encontrados = []
        for raiz, _, archivos in os.walk(settings.MEDIA_ROOT):
            for archivo in archivos:
                encontrados.append(os.path.relpath(os.path.join(raiz, archivo), settings.MEDIA_ROOT))
        return encontrados

    # ── El camino correcto sigue funcionando ──────────────────────────────────

    def test_una_subida_correcta_funciona(self):
        """Con un artículo real, la imagen se guarda (no se ha cerrado de más)."""
        antes = set(self._archivos_en_disco())

        respuesta = self._subir()

        self.assertEqual(respuesta.status_code, 201, respuesta.content)
        self.assertEqual(ItemImage.objects.count(), 1)

        nuevos = set(self._archivos_en_disco()) - antes
        self.assertEqual(len(nuevos), 1, 'debería haberse guardado exactamente un archivo')
        self.assertTrue(
            list(nuevos)[0].startswith('consoles/'),
            f'el archivo debería estar en la carpeta de consolas: {nuevos}',
        )

    def test_se_puede_subir_a_los_tres_tipos(self):
        """Consolas, juegos y accesorios son los tres destinos válidos."""
        from inventory.models.Game import Game

        juego = Game.objects.create(name='Juego con foto')
        casos = [
            ('console', self.consola.id),
            ('game', juego.id),
            ('accessory', self.accesorio.id),
        ]

        for modelo, object_id in casos:
            with self.subTest(modelo=modelo):
                respuesta = self._subir(content_type_model=modelo, object_id=object_id)
                self.assertEqual(respuesta.status_code, 201, respuesta.content)

    # ── Fallo 1: el artículo tiene que existir ────────────────────────────────

    def test_rechaza_un_object_id_que_no_existe(self):
        """
        El fallo principal de E5: antes esto devolvía 201 y creaba una carpeta huérfana
        (`media/consoles/unknown-999999/`).
        """
        respuesta = self._subir(object_id=999999)

        self.assertEqual(respuesta.status_code, 400, respuesta.content)
        self.assertIn('object_id', respuesta.json())
        self.assertEqual(ItemImage.objects.count(), 0, 'no debería haber creado la imagen')

    def test_un_object_id_inexistente_no_deja_archivos(self):
        """Un rechazo no puede dejar basura en el disco."""
        antes = set(self._archivos_en_disco())

        respuesta = self._subir(object_id=999999)

        self.assertEqual(respuesta.status_code, 400, respuesta.content)
        self.assertEqual(
            set(self._archivos_en_disco()) - antes,
            set(),
            'el rechazo ha dejado archivos en el disco',
        )

    def test_el_object_id_debe_ser_del_tipo_indicado(self):
        """
        Un id que existe pero es de OTRO tipo no vale: el id 1 puede ser una consola, pero si
        dices que es un juego y no existe ese juego, se rechaza.
        """
        from inventory.models.Game import Game

        # El accesorio existe, pero decimos que es un juego con ese id
        Game.objects.filter(pk=self.accesorio.id).delete()
        respuesta = self._subir(content_type_model='game', object_id=self.accesorio.id)

        self.assertEqual(respuesta.status_code, 400, respuesta.content)

    # ── Fallo 2: el modelo destino, cerrado ───────────────────────────────────

    def test_rechaza_un_content_type_model_inventado_sin_reventar(self):
        """
        Antes esto daba un **500** con la traza completa de Django (`DoesNotExist`).
        Ahora tiene que ser un 400 limpio.
        """
        respuesta = self._subir(content_type_model='noexiste')

        self.assertEqual(respuesta.status_code, 400, respuesta.content)
        self.assertIn('content_type_model', respuesta.json())

    def test_rechaza_un_modelo_que_no_debe_llevar_fotos(self):
        """
        `missingcomponent` es el catálogo de piezas: existe como modelo, pero no es un artículo
        al que se le suban fotos. Debe rechazarse.
        """
        respuesta = self._subir(content_type_model='missingcomponent', object_id=self.componente.id)

        self.assertEqual(respuesta.status_code, 400, respuesta.content)
        self.assertIn('content_type_model', respuesta.json())

    def test_rechaza_modelos_que_no_son_de_inventario(self):
        """Tampoco vale apuntar a modelos de otras aplicaciones (por ejemplo, usuarios)."""
        for modelo in ('user', 'contenttype', 'session'):
            with self.subTest(modelo=modelo):
                respuesta = self._subir(content_type_model=modelo, object_id=1)
                self.assertEqual(respuesta.status_code, 400, respuesta.content)

    def test_rechaza_si_falta_el_modelo(self):
        """El modelo destino es obligatorio."""
        respuesta = self.client.post(
            '/api/images/',
            data={
                'image': SimpleUploadedFile('foto.png', png_valido(), content_type='image/png'),
                'object_id': self.consola.id,
            },
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
        )

        self.assertEqual(respuesta.status_code, 400, respuesta.content)
        self.assertIn('content_type_model', respuesta.json())

    # ── El otro serializer también valida (se puede usar para crear) ──────────

    def test_el_serializer_de_lectura_tambien_valida(self):
        """
        `ImageSerializer` también acepta escrituras: no puede quedarse sin validar.
        Se le pasa un archivo válido para que la validación llegue al destino.
        """
        from inventory.api.serializers.image import ImageSerializer

        serializer = ImageSerializer(
            data={
                'image': SimpleUploadedFile('foto.png', png_valido(), content_type='image/png'),
                'content_type_model': 'noexiste',
                'object_id': 1,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('content_type_model', serializer.errors)

        serializer = ImageSerializer(
            data={
                'image': SimpleUploadedFile('foto.png', png_valido(), content_type='image/png'),
                'content_type_model': 'console',
                'object_id': 999999,
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn('object_id', serializer.errors)
