from rest_framework.response import Response
from rest_framework.views import APIView
from apps.models.base import Item
from apps.serializers.game import GameSerializer
from rest_framework.decorators import api_view

@api_view(['GET','POST'])
def game_api_view(request):

    if request.method == 'GET':
        games = Item.objects.all()
        games_serializer = GameSerializer(games, many = True)
        return Response(games_serializer.data)

    elif request.method == 'POST':
        game_serializer = GameSerializer(data = request.data)
        if game_serializer.is_valid():
            game_serializer.save()
            return Response(game_serializer.data)
        return Response(game_serializer.errors)