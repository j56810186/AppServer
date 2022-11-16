from django.contrib import admin
from closet.models import Closet, Clothe, Type

# Register your models here.

@admin.register(Closet)
class ClosetAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name', 'user']
    list_filter = ['name', 'user']
    list_display = ['id', 'name', 'user']

@admin.register(Clothe)
class ClotheAdmin(admin.ModelAdmin):
    search_fields = ['name', 'is_formal', 'is_public', 'user', 'closet', 'type']
    list_filter = ['name', 'is_formal', 'is_public', 'user', 'closet', 'type']
    list_display = ['name', 'is_formal', 'is_public', 'user', 'closet', 'type']

@admin.register(Type)
class TypeAdmin(admin.ModelAdmin):
    search_fields = ['id', 'name']
    list_filter = ['name']
    list_display = ['id', 'name']
