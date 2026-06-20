from rest_framework import viewsets, filters
from inventory.models.Console import Console
from inventory.api.serializers.console import ConsoleSerializer


class ConsoleViewSet(viewsets.ModelViewSet):
    queryset = Console.objects.prefetch_related('missing_components', 'images').all()
    serializer_class = ConsoleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'model', 'platform', 'region']
    ordering_fields = ['name', 'platform', 'status', 'created_at', 'price']
    ordering = ['name']