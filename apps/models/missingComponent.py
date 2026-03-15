from django.db import models

class MissingComponent(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Componente faltante"
        verbose_name_plural = "Componentes faltantes"