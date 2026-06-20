from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from .models.Game import Game
from .models.Console import Console
from .models.Accessory import Accessory
from .models.Image import ItemImage
from .models.Missing_component import MissingComponent

class ItemImageInline(GenericTabularInline):
    model = ItemImage
    extra = 1


@admin.register(Console)
class ConsoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'platform', 'region')
    list_filter = ('platform', 'region')
    search_fields = ('name', 'description')
    inlines = [ItemImageInline]
    list_editable = ('price',)


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'platform', 'region')
    list_filter = ('platform', 'region')
    search_fields = ('name', 'description')
    inlines = [ItemImageInline]
    list_editable = ('price',)


@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'platform')
    list_filter = ('platform',)
    search_fields = ('name', 'description')
    inlines = [ItemImageInline]
    list_editable = ('price',)


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'content_type', 'object_id')


@admin.register(MissingComponent)
class MissingComponentAdmin(admin.ModelAdmin):
    list_display = ('id',)