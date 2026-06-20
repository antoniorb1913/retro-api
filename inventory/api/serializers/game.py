from rest_framework import serializers
from inventory.models.Game import Game

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = [
            'id', 'name', 'model', 'platform', 'platform_display',
            'region', 'status', 'status_display', 'description',
            'price', 'acquisition_date', 'complete',
            'missing_components', 'missing_component_ids',
            'images', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']