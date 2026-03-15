from django.db import models
from .base import Item

class ItemImage(models.Model):
    item = models.ForeignKey(
        Item, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(
        'Foto', 
        upload_to='items/%Y/%m/'
    )

    def __str__(self):
        return f"Foto de {self.item.name}"