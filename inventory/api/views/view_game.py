from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from inventory.models.Game import Game
from inventory.api.serializers.game import GameSerializer


class GameViewSet(viewsets.ModelViewSet):
    # Inventario privado: sin token no se lee ni se escribe nada.
    permission_classes = [IsAuthenticated]
    queryset = Game.objects.prefetch_related('missing_components', 'images').all()
    serializer_class = GameSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'model', 'platform', 'region']
    ordering_fields = ['name', 'platform', 'status', 'created_at', 'price', 'total_price']
    ordering = ['name']