from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from inventory.models.Missing_component import MissingComponent
from inventory.api.serializers.missing_component import MissingComponentSerializer

class MissingComponentViewSet(viewsets.ModelViewSet):
    # Inventario privado: sin token no se lee ni se escribe nada.
    permission_classes = [IsAuthenticated]
    queryset = MissingComponent.objects.all()
    serializer_class = MissingComponentSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']