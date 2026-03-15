from django.db import models
from .base import ItemBase
from .console import Console

class Accessory(ItemBase):

    def __str__(self):
        return f"{self.plataform} {self.name}"
    
    class Meta:
        verbose_name = 'Accesorio'
        verbose_name_plural = 'Accesorios'
    