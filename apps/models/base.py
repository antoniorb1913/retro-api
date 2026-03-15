from django.db import models
from .missingComponent import MissingComponent

class ItemBase(models.Model):
    STATUS_CHOICES = [
        ('SEALED', 'Prencitado'),
        ('MINT', 'Como nuevo'),
        ('GOOD', 'Buen estado'),
        ('FAIR', 'Desgastado'),
    ]

    PLATAFORM_CHOICES = [
        # SONY
        ('PS1', 'PlayStation 1'),
        ('PS2', 'PlayStation 2'),
        ('PS3', 'PlayStation 3'),
        ('PS4', 'PlayStation 4'),
        ('PS5', 'PlayStation 5'),
        ('PSP', 'PlayStation Portable'),
        ('PSVITA', 'PlayStation Vita'),

        # NINTENDO SOBREMESA
        ('NES', 'Nintendo Entertainment System'),
        ('SNES', 'Super Nintendo'),
        ('N64', 'Nintendo 64'),
        ('GC', 'Nintendo GameCube'),
        ('WII', 'Nintendo Wii'),
        ('WIIU', 'Nintendo Wii U'),
        ('SWITCH', 'Nintendo Switch'),

        # NINTENDO PORTÁTIL
        ('GB', 'Game Boy'),
        ('GBC', 'Game Boy Color'),
        ('GBA', 'Game Boy Advance'),
        ('DS', 'Nintendo DS'),
        ('3DS', 'Nintendo 3DS'),

        # SEGA
        ('MS', 'Sega Master System'),
        ('MD', 'Sega Mega Drive'),
        ('SS', 'Sega Saturn'),
        ('DC', 'Sega Dreamcast'),
        ('GG', 'Sega Game Gear'),

        # MICROSOFT
        ('XBOX', 'Xbox Original'),
        ('X360', 'Xbox 360'),
        ('XONE', 'Xbox One'),
        ('XSERIES', 'Xbox Series X/S'),

        # RETRO VARIADO / OTRAS
        ('ATARI', 'Atari 2600'),
        ('NEOGEO', 'Neo Geo'),
        ('PCE', 'PC Engine'),
        ('GEN', 'Generica / PC'),
    ]
    
    name = models.CharField(
        'nombre',
        max_length=200
    )

    acquisition_date = models.DateField(
        'fecha de adquisición',
        null=True, 
        blank=True
    )

    price = models.DecimalField(
        'precio de compra',
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )

    status = models.CharField(
        'estado',
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='GOOD'
    )

    description = models.TextField(
        'descripción',
        max_length=255, 
        blank=True, 
        null = True
    )

    region = models.CharField(
        'region',
        max_length=10, 
        default='PAL', 
        blank = True, 
        null = True
    )

    plataform = models.CharField(
        max_length=20, 
        choices=PLATAFORM_CHOICES, 
        null=True, 
        blank=True
    )
    
    missing_components = models.ManyToManyField(
        MissingComponent,
        blank=True,
        verbose_name='Falta específicamente:'
    )
    
    complete = models.BooleanField(
        '¿Completo?',
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Añadido el"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Última modificación"
    )
    
    class Meta:
        abstract = True

class Item(ItemBase):
    pass