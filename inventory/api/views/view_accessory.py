from rest_framework import viewsets, filters
from inventory.models.Accessory import Accessory
from inventory.api.serializers.accessory import AccessorySerializer


class AccessoryViewSet(viewsets.ModelViewSet):
    queryset = Accessory.objects.prefetch_related('missing_components', 'images').all()
    serializer_class = AccessorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'model', 'platform', 'region']
    ordering_fields = ['name', 'platform', 'status', 'created_at', 'price']
    ordering = ['name']