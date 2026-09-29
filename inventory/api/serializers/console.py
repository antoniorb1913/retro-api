from urllib.parse import urlparse

from rest_framework import serializers
from inventory.models.Console import Console
from inventory.models.Missing_component import MissingComponent
from inventory.api.serializers.missing_component import MissingComponentSerializer
from inventory.api.serializers.image import ImageSerializer

class ConsoleSerializer(serializers.ModelSerializer):
    missing_components = MissingComponentSerializer(many=True, read_only=True)
    missing_component_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=MissingComponent.objects.all(),
        write_only=True,
        source='missing_components',
        required=False,
    )
    images = ImageSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)

    class Meta:
        model = Console
        fields = [
            'id', 'name', 'model', 'platform', 'platform_display',
            'region', 'status', 'status_display', 'description',
            'price', 'total_price', 'purchase_url', 'store', 'protective', 'acquisition_date', 'complete', 'edition',
            'missing_components', 'missing_component_ids',
            'images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        """
        Reglas del total:
          - Si no se indica, se copia el precio del artículo (no hay gastos añadidos).
          - Si se indica y es menor que el precio del artículo, se rechaza: el total incluye
            el artículo más envío y gastos, así que nunca puede ser menor.
        """
        price = attrs.get('price', getattr(self.instance, 'price', None))
        total_price = attrs.get('total_price', getattr(self.instance, 'total_price', None))

        if total_price in (None, '') and price not in (None, ''):
            attrs['total_price'] = price
        elif total_price not in (None, '') and price not in (None, '') and total_price < price:
            raise serializers.ValidationError({
                'total_price': 'El total no puede ser menor que el precio del artículo.',
            })

        return attrs

    def validate_purchase_url(self, value):
        """
        Solo se aceptan enlaces web con http o https. Se rechaza cualquier otro esquema
        (`javascript:`, `data:`, `file:`...): ese enlace se pinta en el frontend y un esquema
        peligroso sería un vector de ataque.
        """
        if not value:
            return value

        esquema = urlparse(value).scheme.lower()
        if esquema not in ('http', 'https'):
            raise serializers.ValidationError(
                'El enlace debe empezar por http:// o https://.'
            )

        return value
