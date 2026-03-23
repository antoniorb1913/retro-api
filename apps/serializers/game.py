from rest_framework import serializers
from apps.models.base import Item

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'