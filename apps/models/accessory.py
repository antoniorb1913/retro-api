from django.db import models
from .base import Item

class Accessory(Item):

    def __str__(self):
        return f"{self.plataform} {self.name}"
    
    class Meta:
        verbose_name = 'Accesorio'
        verbose_name_plural = 'Accesorios'
    