import os
import io
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.core.files.base import ContentFile
from PIL import Image

class ItemImage(models.Model):
    """
    Modelo Genérico para la gestión de imágenes optimizadas en WebP.
    Se puede enlazar a cualquier modelo del proyecto (Consolas, Juegos, etc.)
    sin modificar la estructura de la base de datos.
    """
    # Relación Genérica (Camaleónica)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Almacenamiento organizado dinámicamente por año y mes
    image = models.ImageField('Foto', upload_to='items/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.image:
            name = self.image.name.lower()
            
            # Filtro inteligente: Si NO es webp, lo convertimos
            if not name.endswith('.webp'):
                # 1. Abrimos la imagen original (HEIC, PNG, JPG, etc.) con Pillow
                img = Image.open(self.image)
                
                # 2. Homogeneizamos el espectro de color al estándar RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # 3. Procesamos y comprimimos a WebP usando la memoria RAM
                output = io.BytesIO()
                img.save(output, format='WEBP', quality=80)
                output.seek(0)
                
                # 4. Modificamos la extensión del nombre del archivo por fuera
                new_name = self.image.name.rsplit('.', 1)[0] + '.webp'
                
                # 5. Sustituimos el archivo original por el nuevo WebP real en memoria
                self.image = ContentFile(output.read(), name=new_name)

        # 6. Pasamos el testigo a Django para el guardado físico y en Postgres
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Foto de {self.content_object}"

    class Meta:
        verbose_name = "Imagen"
        verbose_name_plural = "Imágenes"
        ordering = ['-uploaded_at']


# ──────────────────────────────────────────────────────────────────────
# SEÑALES (SIGNALS) AUTOMÁTICAS PARA MANTENER EL ALMACENAMIENTO LIMPIO
# ──────────────────────────────────────────────────────────────────────

@receiver(post_delete, sender=ItemImage)
def delete_image_file_on_delete(sender, instance, **kwargs):
    """
    Se activa JUSTO DESPUÉS de borrar el registro en la base de datos.
    Elimina de forma física el archivo .webp del disco para no dejar huérfanos.
    """
    if instance.image and os.path.isfile(instance.image.path):
        os.remove(instance.image.path)


@receiver(pre_save, sender=ItemImage)
def delete_old_image_file_on_change(sender, instance, **kwargs):
    """
    Se activa JUSTO ANTES de actualizar un registro existente.
    Si el usuario cambia una foto vieja por una nueva, detecta el cambio
    y destruye el archivo físico anterior para evitar la acumulación de basura.
    """
    # Si el objeto es nuevo (no tiene Clave Primaria todavía), salimos
    if not instance.pk:
        return False  

    try:
        # Obtenemos el estado de la foto tal y como estaba antes en la base de datos
        old_image = sender.objects.get(pk=instance.pk).image
    except sender.DoesNotExist:
        return False

    new_image = instance.image
    # Si la foto anterior existe y es distinta de la nueva que se va a guardar...
    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path) # Destruimos la foto antigua en el disco