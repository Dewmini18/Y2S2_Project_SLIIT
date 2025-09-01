from django.contrib import admin
from .models import Payment, PaymentItem

class PaymentItemInline(admin.TabularInline):
    
    model = PaymentItem
    readonly_fields = ['medicine', 'quantity', 'price', 'total_price']
    extra = 0 # No extra blank forms by default

class PaymentAdmin(admin.ModelAdmin):
    """
    Custom admin class for the Payment model.
    """
    # Display these fields in the list view
    list_display = ['id', 'patient', 'prescription', 'total_amount', 'status', 'payment_date']
    
    # Enable filtering by these fields in the list view
    list_filter = ['status', 'payment_date']
    
    # Enable searching by patient name and prescription ID
    search_fields = ['patient__first_name', 'patient__last_name', 'prescription__id']
    
    # Use the PaymentItemInline to show related items
    inlines = [PaymentItemInline]
    
    # Make fields readonly to prevent accidental modification in the admin
    readonly_fields = ['patient', 'prescription', 'total_amount', 'payment_date']


# Register your models with the custom admin classes
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentItem)
