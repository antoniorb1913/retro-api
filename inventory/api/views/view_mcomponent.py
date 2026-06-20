from rest_framework import viewsets, filters
from inventory.models.Missing_component import MissingComponent
from inventory.api.serializers.missing_component import MissingComponentSerializer

class MissingComponentViewSet(viewsets.ModelViewSet):
    queryset = MissingComponent.objects.all()
    serializer_class = MissingComponentSerializer
    
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']