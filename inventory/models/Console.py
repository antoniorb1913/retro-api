from django.db import models
from .Base import ItemBase


class Console(ItemBase):
    edition = models.CharField(max_length=100, blank=True, default='')

    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"