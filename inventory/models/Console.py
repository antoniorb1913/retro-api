from django.db import models
from .Base import ItemBase


class Console(ItemBase):
    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"