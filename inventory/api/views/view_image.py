from rest_framework import viewsets, parsers
from rest_framework.permissions import IsAuthenticated

from inventory.models.Image import ItemImage
from inventory.api.serializers.image import ImageSerializer, ImageUploadSerializer
from user.api.throttles import ThrottleConExencionStaff

class ItemImageViewSet(viewsets.ModelViewSet):
    """
    Endpoint de imágenes — acepta multipart/form-data para subida.
    """
    # Inventario privado: sin token no se lee, no se sube y no se borra ninguna imagen.
    permission_classes = [IsAuthenticated]
    # Freno de intentos (tarea E6): cada subida convierte a WebP y escribe en disco, así que se
    # limita a `subida` por hora (el número está en `DEFAULT_THROTTLE_RATES`).
    throttle_classes = [ThrottleConExencionStaff]
    throttle_scope = 'subida'
    # Evita el N+1 trayendo los tipos de contenido de golpe
    queryset = ItemImage.objects.select_related('content_type').all()
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ImageUploadSerializer
        return ImageSerializer

    def perform_destroy(self, instance):
        # ⚡ LIMPIEZA: Evita dejar imágenes huérfanas en el disco/Docker al borrar
        if instance.image:
            instance.image.delete(save=False)
        super().perform_destroy(instance)