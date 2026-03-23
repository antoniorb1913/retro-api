from django.db import models

class ItemImage(models.Model):
    # Relaciones opcionales a cada tipo de objeto
    game = models.ForeignKey(
        'apps.Game', 
        on_delete=models.CASCADE, 
        related_name='images', 
        null=True, 
        blank=True
    )
    console = models.ForeignKey(
        'apps.Console', 
        on_delete=models.CASCADE, 
        related_name='images', 
        null=True, 
        blank=True
    )
    accessory = models.ForeignKey(
        'apps.Accessory', 
        on_delete=models.CASCADE, 
        related_name='images', 
        null=True, 
        blank=True
    )

    image = models.ImageField(
        'Foto', 
        upload_to='items/%Y/%m/'
    )

    def __str__(self):
        # Un pequeño truco para que el nombre en el admin sea útil
        obj = self.game or self.console or self.accessory
        return f"Foto de {obj.name if obj else 'desconocido'}"

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"