# from django.shortcuts import get_object_or_404, render
# from .models import Product
# from django.db import models


# # Homepage view
# def online_store_homepage(request):
#     """
#     Display the online store homepage with featured products
#     """
#     # Get featured products for homepage display
#     featured_products = Product.objects.filter(
#         featured=True, 
#         available_online=True
#     )[:6]  # Limit to 6 featured products
    
#     context = {
#         'featured_products': featured_products
#     }
#     return render(request, 'onlineStore/homepage.html', context)


# # Product listing view
# def products(request):
#     """
#     Display all products with filtering options
#     """
#     # Get all available online products
#     products = Product.objects.filter(available_online=True)
    
#     # Get filter parameters from request
#     product_type = request.GET.get('type')  # 'medicine' or 'non_medical'
#     category = request.GET.get('category')
#     search_query = request.GET.get('search', '').strip()
#     sort_by = request.GET.get('sort', 'name')  # default sort by name
    
#     # Apply filters
#     if product_type:
#         products = products.filter(product_type=product_type)
    
#     # Filter by category (requires checking the linked model)
#     if category:
#         if product_type == 'medicine':
#             products = products.filter(medicine__category=category)
#         elif product_type == 'non_medical':
#             products = products.filter(non_medical_product__category=category)
    
#     # Search functionality
#     if search_query:
#         # Search in both medicine and non-medical product names
#         products = products.filter(
#             models.Q(medicine__name__icontains=search_query) |
#             models.Q(medicine__brand__icontains=search_query) |
#             models.Q(non_medical_product__name__icontains=search_query) |
#             models.Q(non_medical_product__brand__icontains=search_query)
#         )
    
#     # Sorting
#     if sort_by == 'price_low':
#         # Custom sorting since price is in related models
#         products = sorted(products, key=lambda p: p.get_price())
#     elif sort_by == 'price_high':
#         products = sorted(products, key=lambda p: p.get_price(), reverse=True)
#     elif sort_by == 'name':
#         products = sorted(products, key=lambda p: p.get_name())
    
#     # Get categories for filter dropdown
#     medicine_categories = []
#     non_medical_categories = []
    
#     if not product_type or product_type == 'medicine':
#         # Get unique medicine categories
#         from Medicine_inventory.models import Medicine
#         medicine_categories = Medicine.CATEGORY_CHOICES
    
#     if not product_type or product_type == 'non_medical':
#         # Get unique non-medical categories
#         from Non_Medicine_inventory.models import NonMedicalProduct
#         non_medical_categories = NonMedicalProduct.CATEGORY_CHOICES
    
#     context = {
#         'products': products,
#         'medicine_categories': medicine_categories,
#         'non_medical_categories': non_medical_categories,
#         'current_type': product_type,
#         'current_category': category,
#         'search_query': search_query,
#         'current_sort': sort_by,
#     }
    
#     return render(request, 'onlineStore/products.html', context)


# # Product detail view
# def product_detail(request, pk):
#     """
#     Display detailed information about a specific product
#     """
#     product = get_object_or_404(Product, pk=pk, available_online=True)
    
#     # Get related products (same category)
#     related_products = Product.objects.filter(
#         available_online=True,
#         product_type=product.product_type
#     ).exclude(pk=pk)[:4]  # Show 4 related products
    
#     # Additional product information based on type
#     additional_info = {}
#     if product.medicine:
#         additional_info = {
#             'dosage': product.medicine.dosage,
#             'category': product.medicine.category,
#             'medicine_type': product.medicine.medicine_type,
#             'description': product.medicine.description,
#             'requires_prescription': product.medicine.medicine_type == 'RX',
#         }
#     elif product.non_medical_product:
#         additional_info = {
#             'category': product.non_medical_product.category,
#             'description': product.non_medical_product.description,
#         }
    
#     context = {
#         'product': product,
#         'related_products': related_products,
#         'additional_info': additional_info,
#     }
    
#     return render(request, 'onlineStore/product_detail.html', context)


# onlineStore/views.py

from django.shortcuts import get_object_or_404, render
from .models import Product
from django.db.models import Q
from django.db.models.functions import Coalesce

# NOTE: Moved inventory imports to the top for better practice
from Medicine_inventory.models import Medicine
from Non_Medicine_inventory.models import NonMedicalProduct

# Homepage view (Your code was fine)
def online_store_homepage(request):
    featured_products = Product.objects.filter(
        featured=True, 
        available_online=True
    ).select_related('medicine', 'non_medical_product')[:6]
    
    context = {
        'featured_products': featured_products
    }
    return render(request, 'onlineStore/homepage.html', context)

# Product listing view (Refactored for performance and clarity)
def products(request):
    products = Product.objects.filter(available_online=True).select_related(
        'medicine', 'non_medical_product'
    )
    
    product_type = request.GET.get('type', '')
    category = request.GET.get('category', '')
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'name')
    
    if product_type:
        products = products.filter(product_type=product_type)
    
    if category:
        # Filter across both related models using Q objects
        products = products.filter(
            Q(medicine__category=category) | 
            Q(non_medical_product__category=category)
        )
    
    if search_query:
        products = products.filter(
            Q(medicine__name__icontains=search_query) |
            Q(medicine__brand__icontains=search_query) |
            Q(non_medical_product__name__icontains=search_query) |
            Q(non_medical_product__brand__icontains=search_query)
        )
    
    # --- PERFORMANCE FIX: Sort in the database, not in Python ---
    # Annotate creates a temporary column in the database for sorting.
    # Coalesce picks the first non-null value, unifying the fields.
    products = products.annotate(
        current_price=Coalesce('medicine__selling_price', 'non_medical_product__selling_price'),
        current_name=Coalesce('medicine__name', 'non_medical_product__name')
    )

    if sort_by == 'price_low':
        products = products.order_by('current_price')
    elif sort_by == 'price_high':
        products = products.order_by('-current_price')
    else: # Default sort by name
        products = products.order_by('current_name')
    
    # Get categories for filter dropdown
    medicine_categories = Medicine.CATEGORY_CHOICES
    non_medical_categories = NonMedicalProduct.CATEGORY_CHOICES
    
    context = {
        'products': products,
        'medicine_categories': medicine_categories,
        'non_medical_categories': non_medical_categories,
        'current_type': product_type,
        'current_category': category,
        'search_query': search_query,
        'current_sort': sort_by,
    }
    
    return render(request, 'onlineStore/products.html', context)


# Product detail view (Simplified)
from django.shortcuts import get_object_or_404, render
from .models import Product

def product_detail(request, pk):
    """
    Display detailed information about a specific product.
    """
    product = get_object_or_404(
        Product.objects.select_related('medicine', 'non_medical_product'), 
        pk=pk, 
        available_online=True
    )
    
    related_products = []
    # Get the actual linked inventory item to find its category
    inventory_item = product.medicine or product.non_medical_product

    if inventory_item:
        # We need to use the lowercase field name ('medicine' or 'non_medical_product')
        # for the database query. The model's product_type field has the wrong case.
        
        # FIX: Explicitly use the lowercase field name for the query lookup.
        # We also need to map the model's Choice value to the field name.
        product_type_field_name = 'medicine' if product.product_type == 'Medicine' else 'non_medical_product'

        related_products = Product.objects.filter(
            available_online=True,
            product_type=product.product_type,
            # This is the corrected dynamic filter
            **{f'{product_type_field_name}__category': inventory_item.category}
        ).exclude(pk=pk)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'onlineStore/product_detail.html', context)