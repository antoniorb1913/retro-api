from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from .Missing_component import MissingComponent
from inventory.models.Image import ItemImage

class ItemBase(models.Model):
    STATUS_CHOICES = [
        ('SEALED', 'Precintado'),
        ('MINT', 'Como nuevo'),
        ('GOOD', 'Buen estado'),
        ('FAIR', 'Desgastado'),
    ]

    PLATFORM_CHOICES = [
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
        max_length=200
    )
    
    model = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )
    
    acquisition_date = models.DateField(
        blank=True,
        null=True
    )
    
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='GOOD'
    )
    
    description = models.TextField(
        blank=True, 
        null=True
    )
    
    region = models.CharField(
        max_length=20,
        default='PAL ESPAÑA', 
        blank=True, 
        null=True
    )
    
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        blank=True, 
        null=True
    )
    
    missing_components = models.ManyToManyField(
        MissingComponent,
        blank=True,
    )
    
    complete = models.BooleanField(
        default=False
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    images = GenericRelation(ItemImage)
    
    class Meta:
        abstract = True  # Así no crea una tabla para ItemBase, solo para sus hijos
        
    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"