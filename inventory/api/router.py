from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.view_accessory import AccessoryViewSet
from .views.view_console import ConsoleViewSet
from .views.view_game import GameViewSet
from .views.view_image import ItemImageViewSet
from .views.view_mcomponent import MissingComponentViewSet

router = DefaultRouter()
router.register(r'consoles', ConsoleViewSet, basename='console')
router.register(r'games', GameViewSet, basename='game')
router.register(r'accessories', AccessoryViewSet, basename='accessory')
router.register(r'images', ItemImageViewSet, basename='image')
router.register(r'components', MissingComponentViewSet, basename='component')

urlpatterns = [
    path('', include(router.urls)),
]
