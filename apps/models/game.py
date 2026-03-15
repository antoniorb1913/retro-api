from django.db import models
from .base import Item

class Game(Item):

    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        verbose_name = 'Juego'
        verbose_name_plural = 'Juegos'