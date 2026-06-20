from rest_framework import serializers
from inventory.models.Missing_component import MissingComponent

class MissingComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissingComponent
        fields = ['id', 'name']