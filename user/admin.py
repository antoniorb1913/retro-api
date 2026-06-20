from django.contrib import admin
from user.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


@admin.register(User) # --> Decorador

class UserAdmin(BaseUserAdmin):
    # Organizar, agrupar y maquetar visualmente los campos dentro del formulario
    fieldsets = [
        (None, {'fields': ('username', 'password')}),
        ('Person Information', {'fields': ('first_name', 'last_name', 'email')}),
        ('permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    ]
    
    # Datos que queremos que se muestren en el dashboard
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff')
    # Por que datos se puede buscar
    search_fields = ('email', 'username', 'first_name', 'last_name')
    # Con que campo queremos que se orden los usuarios
    ordering = ('email',)