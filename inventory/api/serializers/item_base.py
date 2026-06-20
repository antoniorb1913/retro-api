from rest_framework import serializers
from inventory.models.Missing_component import MissingComponent
from inventory.models.Image import ItemImage
# Asegúrate de importar tus serializers correspondientes
from .missing_component import MissingComponentSerializer
from .image import ImageSerializer
from .item_base import ItemBase

class ItemBaseSerializer(serializers.ModelSerializer):
    # Gestión de componentes (Lectura completa / Escritura por IDs)
    missing_components = MissingComponentSerializer(many=True, read_only=True)
    missing_component_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=MissingComponent.objects.all(),
        write_only=True,
        source='missing_components',
        required=False,
    )
    
    # DRF mapea la GenericRelation de forma nativa
    # y pasa el contexto 'request' automáticamente para generar las URLs de las fotos
    images = ImageSerializer(many=True, read_only=True)
    
    # Mapeo de los nombres legibles de los ChoiceFields (enums)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = ItemBase
        fields = [
            'id', 
            'missing_components', 
            'missing_component_ids', 
            'images', 
            'status_display', 
            'platform_display'
        ]