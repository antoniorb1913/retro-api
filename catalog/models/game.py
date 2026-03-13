from django.db import models
from .console import Console
from .base import ItemBase

class Game(ItemBase):
    plataform = models.ForeignKey(
        Console, 
        on_delete=models.CASCADE, 
        related_name="game_list"
    )
    
    gender = models.CharField(
        max_length=50, 
        blank=True, 
        null = True
    )

    def __str__(self):
        return f"{self.name} ({self.consola.name})"