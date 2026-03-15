from django.db import models
from .console import ItemBase
from .base import ItemBase

class Game(ItemBase):

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name = 'Juego'
        verbose_name_plural = 'Juegos'