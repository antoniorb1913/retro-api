from django.urls import path
from apps.serializers.api import game_api_view

urlpatterns = [
    path('game/', game_api_view, name = 'usuario_api')
]
