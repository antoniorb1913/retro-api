from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from inventory.models.Image import ItemImage

class ImageSerializer(serializers.ModelSerializer):
    # Aseguramos que el nombre sea consistente en todo el archivo
    content_type_model = serializers.CharField(write_only=True)
    object_id = serializers.IntegerField()
    
    class Meta:
        model = ItemImage
        fields = ['id', 'image', 'content_type_model', 'object_id', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at'] # Asegúrate de que coincidan con tu modelo real
        
    def validate_content_type_model(self, value):
        """
        Validación limpia: Si el modelo no existe en la app, 
        devolvemos un error 400 controlado en vez de romper el servidor.
        """
        try:
            return ContentType.objects.get(app_label='inventory', model=value.lower())
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(
                f"El modelo '{value}' no existe en la aplicación 'inventory'."
            )
        
    def create(self, validated_data):
        # Como ya lo validamos arriba, aquí 'content_type_model' ya es una instancia de ContentType
        content_type = validated_data.pop('content_type_model')
        validated_data['content_type'] = content_type
        
        return super().create(validated_data)


class ImageUploadSerializer(serializers.ModelSerializer):
    """Serializer para subida de imágenes vía multipart/form-data"""
    content_type_model = serializers.CharField(write_only=True)  # 'game', 'console', 'accessory'
    object_id = serializers.IntegerField()

    class Meta:
        model = ItemImage
        fields = ['id', 'image', 'content_type_model', 'object_id', 'uploaded_at']
        read_only_fields = ['uploaded_at']

    def create(self, validated_data):
        model_name = validated_data.pop('content_type_model')
        content_type = ContentType.objects.get(app_label='inventory', model=model_name.lower())
        validated_data['content_type'] = content_type
        return super().create(validated_data)