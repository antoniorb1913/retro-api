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
            'price', 'acquisition_date', 'complete', 'edition',
            'missing_components', 'missing_component_ids',
            'images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']
