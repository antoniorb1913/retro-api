"""
Serializers del endpoint de imágenes.

Aquí se concentran las dos reglas de validación que comparten los dos serializers, para que no
pueda quedar uno sin proteger. Pasó en E5: `ImageUploadSerializer` (el que se usa al subir) no
validaba nada.

Reglas:
  1. Solo se admiten tres destinos: consolas, juegos y accesorios. Antes valía cualquier texto y
     un modelo inexistente reventaba con `DoesNotExist` (un 500 con la traza de Django).
  2. El artículo destino tiene que existir de verdad. Antes se aceptaba cualquier `object_id` y se
     creaba una carpeta huérfana en el disco (`media/consoles/unknown-999999/...`).
"""
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

from inventory.models.Image import ItemImage

# Los únicos modelos que pueden llevar fotos.
MODELOS_CON_IMAGENES = ('console', 'game', 'accessory')

# Mensaje único para los dos serializers.
MENSAJE_DESTINO_INVALIDO = 'Solo se admiten imágenes de consolas, juegos o accesorios.'


class ImagenDestinoValidoMixin:
    """
    Validación compartida: el destino de la imagen tiene que ser un artículo real y de un tipo
    permitido. Se aplica igual al crear y al consultar, porque los dos serializers aceptan
    escrituras.
    """

    def validate(self, attrs):
        """
        Comprueba que `object_id` corresponde a un artículo que existe del tipo indicado.

        En una actualización parcial que no envía el destino no hay nada que comprobar, así que se
        usa el valor que ya tenía la imagen.
        """
        content_type_model = attrs.get(
            'content_type_model',
            getattr(self.instance, 'content_type_model', None),
        )
        object_id = attrs.get('object_id', getattr(self.instance, 'object_id', None))

        if not content_type_model or object_id in (None, ''):
            return attrs

        # El modelo ya pasó la lista blanca del `ChoiceField`, así que aquí siempre existe.
        content_type = ContentType.objects.get(app_label='inventory', model=content_type_model)
        modelo_destino = content_type.model_class()

        if modelo_destino is None or not modelo_destino.objects.filter(pk=object_id).exists():
            raise serializers.ValidationError({
                'object_id': f'No existe ningún artículo con el id {object_id} de ese tipo.',
            })

        return attrs


class ImageSerializer(ImagenDestinoValidoMixin, serializers.ModelSerializer):
    """
    Serializer de lectura de imágenes. También acepta escrituras, de ahí que valide igual que el
    de subida.
    """
    content_type_model = serializers.ChoiceField(
        choices=MODELOS_CON_IMAGENES,
        write_only=True,
        error_messages={'invalid_choice': MENSAJE_DESTINO_INVALIDO},
    )
    object_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = ItemImage
        fields = ['id', 'image', 'content_type_model', 'object_id', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']

    def create(self, validated_data):
        # El modelo destino ya está validado y es una cadena de la lista blanca.
        validated_data['content_type'] = ContentType.objects.get(
            app_label='inventory',
            model=validated_data.pop('content_type_model'),
        )
        return super().create(validated_data)


class ImageUploadSerializer(ImagenDestinoValidoMixin, serializers.ModelSerializer):
    """Serializer para subida de imágenes vía multipart/form-data."""
    content_type_model = serializers.ChoiceField(
        choices=MODELOS_CON_IMAGENES,
        write_only=True,
        error_messages={'invalid_choice': MENSAJE_DESTINO_INVALIDO},
    )
    object_id = serializers.IntegerField(min_value=1)

    class Meta:
        model = ItemImage
        fields = ['id', 'image', 'content_type_model', 'object_id', 'uploaded_at']
        read_only_fields = ['uploaded_at']

    def create(self, validated_data):
        validated_data['content_type'] = ContentType.objects.get(
            app_label='inventory',
            model=validated_data.pop('content_type_model'),
        )
        return super().create(validated_data)
