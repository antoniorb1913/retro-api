from inventory.models.Console import Console
from inventory.models.Game import Game
from inventory.models.Accessory import Accessory
from inventory.models.Missing_component import MissingComponent

print(f'Consolas: {Console.objects.count()}')
print(f'Juegos: {Game.objects.count()}')
print(f'Accesorios: {Accessory.objects.count()}')
print(f'Componentes faltantes: {MissingComponent.objects.count()}')