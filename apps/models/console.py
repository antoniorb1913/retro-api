from django.db import models
from .base import ItemBase

class Console(ItemBase):

    def __str__(self):
            return f"{self.plataform}"
        

    class Meta:
        verbose_name = 'Consola'
        verbose_name_plural = 'Consolas'