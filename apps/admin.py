from django.contrib import admin
from .models.console import Console
from .models.game import Game
from .models.accessory import Accessory
from import_export import resources
from import_export.admin import ImportExportModelAdmin




class ConsoleResource(resources.ModelResource):
    class Meta:
        model = Console

@admin.register(Console)

class ConsoleAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'plataform', 'region', 'status', 'complete')
    list_filter = ('plataform', 'status')
    search_fields = ('name',)
    resource_class = ConsoleResource



class GameResource(resources.ModelResource):
    class Meta:
        model = Game

@admin.register(Game)

class GameAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'plataform', 'status', 'complete')
    list_filter = ('plataform', 'status', 'complete')
    search_fields = ('name',)
    resource_class = GameResource


class AccessoryResource(resources.ModelResource):
    class Meta:
        model = Accessory

@admin.register(Accessory)

class AccessoryAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'plataform', 'status', 'complete')
    list_filter = ('plataform', 'status', 'complete')
    search_fields = ('name',)
    resource_class = AccessoryResource