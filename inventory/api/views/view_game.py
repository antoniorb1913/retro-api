from rest_framework import viewsets, filters
from inventory.models.Game import Game
from inventory.api.serializers.game import GameSerializer


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.prefetch_related('missing_components', 'images').all()
    serializer_class = GameSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'model', 'platform', 'region']
    ordering_fields = ['name', 'platform', 'status', 'created_at', 'price']
    ordering = ['name']