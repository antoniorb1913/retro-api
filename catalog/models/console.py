from django.db import models
from .base import ItemBase

class Console(ItemBase):

    plataform = models.CharField(
        'fabricante',
        max_length=50
    )
    

def __str__(self):
        return f"{self.plataform} {self.nombre} [{self.region}]"
    