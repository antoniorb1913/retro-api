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
    list_display = ('id', 'name', 'price', 'total_price', 'store', 'platform', 'region')
    list_filter = ('platform', 'region')
    search_fields = ('name', 'description')
    inlines = [ItemImageInline]
    list_editable = ('price', 'total_price')
    # `purchase_url` se edita en la ficha del artículo, no en la lista: es una URL larga.
    fields = ('name', 'edition', 'model', 'platform', 'region', 'status', 'description',
              'price', 'total_price', 'purchase_url', 'acquisition_date', 'store',
              'protective', 'complete', 'missing_components')


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'total_price', 'store', 'platform', 'region')
    list_filter = ('platform', 'region')
    search_fields = ('name', 'description')
    inlines = [ItemImageInline]
    list_editable = ('price', 'total_price')
    # `purchase_url` se edita en la ficha del artículo, no en la lista: es una URL larga.
    fields = ('name', 'edition', 'model', 'platform', 'region', 'status', 'description',
              'price', 'total_price', 'purchase_url', 'acquisition_date', 'store',
              'protective', 'complete', 'missing_components')


@admin.register(Accessory)
class AccessoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'total_price', 'store', 'platform')
    list_filter = ('platform',)
    search_fields = ('name', 'description')
    inlines = [ItemImageInline]
    list_editable = ('price', 'total_price')
    # `purchase_url` se edita en la ficha del artículo, no en la lista: es una URL larga.
    fields = ('name', 'model', 'platform', 'region', 'status', 'description',
              'price', 'total_price', 'purchase_url', 'acquisition_date', 'store',
              'protective', 'complete', 'missing_components')


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image', 'content_type', 'object_id')


@admin.register(MissingComponent)
class MissingComponentAdmin(admin.ModelAdmin):
    list_display = ('id',)