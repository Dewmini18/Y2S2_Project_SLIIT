from django.contrib import admin
from Medicine_inventory.models import Medicine
from .models import NonMedicalProduct


@admin.register(NonMedicalProduct)
class NonMedicalProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'brand', 'category', 'cost_price', 'selling_price',
        'stock', 'reorder_level', 'is_active', 'created_at',
        'updated_at'
    ]
    search_fields = ['name', 'brand', 'category', 'description']
    list_filter = ['category', 'is_active', 'brand']
    ordering = ['name', 'brand']
    readonly_fields = ['created_at', 'updated_at', 'slug']
    prepopulated_fields = {'slug': ('name',)}