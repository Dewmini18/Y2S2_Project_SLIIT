from django.contrib import admin
from .models import Product


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 
        'product_type', 
        'available_online', 
        'featured', 
        'price', 
        'stock'  
    )
    list_filter = ('product_type', 'available_online', 'featured')
    search_fields = ('medicine__name', 'non_medical_product__name')
    
    # These are your model's helper methods
    @admin.display(description='Price')
    def price(self, obj):
        return obj.price

    @admin.display(description='Stock')
    def stock(self, obj):
        return obj.stock