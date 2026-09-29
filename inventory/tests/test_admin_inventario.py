"""
Tests de la configuración del admin de inventario.

El admin permite declarar una lista explícita de campos (`fields`). Si un nombre de esa lista no
existe en el modelo, Django **no falla al arrancar** (`manage.py check` no dice nada): revienta con
`FieldError: Unknown field(s) (…) specified for …` al abrir la página de ese modelo. Es decir, el
fallo solo se ve al entrar en el admin, y con un 500 en la cara.

Estos tests abren las páginas del admin de verdad, que es la única forma de cubrirlo.

Ejecutar solo estos tests:
    docker compose exec api python manage.py test inventory.tests.test_admin_inventario
"""
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class AdminInventarioTests(TestCase):
    """Las páginas del admin de inventario se construyen sin errores."""

    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            email='admin.inventario@example.com',
            username='admin_inventario',
            password='ClaveDePrueba123!',
        )

    def setUp(self):
        # `SERVER_NAME` evita el error DisallowedHost al no usar el host de pruebas por defecto.
        self.client = Client(SERVER_NAME='localhost')
        self.client.force_login(self.admin)

    def test_los_formularios_declarados_usan_campos_reales(self):
        """
        Cada campo declarado en el admin debe existir en su modelo.

        Si alguien añade un campo mal escrito (o lo copia de otro modelo, como `edition` en
        Accessory), este test lo caza antes de que llegue a producción.
        """
        from django.contrib import admin

        from inventory.models.Accessory import Accessory
        from inventory.models.Console import Console
        from inventory.models.Game import Game

        for modelo in (Console, Game, Accessory):
            with self.subTest(modelo=modelo.__name__):
                modelo_admin = admin.site._registry[modelo]
                declarados = set(modelo_admin.get_fields(None) or [])
                reales = {campo.name for campo in modelo._meta.get_fields()}

                desconocidos = declarados - reales
                self.assertEqual(
                    desconocidos,
                    set(),
                    f'{modelo.__name__} declara campos que no existen: {sorted(desconocidos)}',
                )

    def test_las_paginas_del_admin_de_inventario_abren(self):
        """Las seis páginas (listado y alta de cada recurso) responden sin error."""
        rutas = [
            '/admin/inventory/console/',
            '/admin/inventory/console/add/',
            '/admin/inventory/game/',
            '/admin/inventory/game/add/',
            '/admin/inventory/accessory/',
            '/admin/inventory/accessory/add/',
        ]

        for ruta in rutas:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertEqual(respuesta.status_code, 200, f'{ruta} no responde correctamente')

    def test_el_enlace_de_compra_se_puede_editar_desde_el_admin(self):
        """El campo nuevo de D2 está en el formulario del admin, no solo en la API."""
        from django.contrib import admin

        from inventory.models.Console import Console
        from inventory.models.Game import Game
        from inventory.models.Accessory import Accessory

        for modelo in (Console, Game, Accessory):
            with self.subTest(modelo=modelo.__name__):
                campos = admin.site._registry[modelo].get_fields(None)
                self.assertIn('purchase_url', campos)
