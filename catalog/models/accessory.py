from django.db import models
from .base import ItemBase
from .console import Console

class Accessory(ItemBase):

    plataform = models.ForeignKey(
        Console, 
        on_delete=models.CASCADE, 
        related_name="accesorios_list"
    )

    def __str__(self):
        return f"{self.fabricante} {self.nombre}"
    