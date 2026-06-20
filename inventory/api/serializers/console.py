from rest_framework import serializers
from inventory.models.Console import Console

class ConsoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Console
        fields = [
            'id', 'name', 'model', 'platform', 'platform_display',
            'region', 'status', 'status_display', 'description',
            'price', 'acquisition_date', 'complete',
            'missing_components', 'missing_component_ids',
            'images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']