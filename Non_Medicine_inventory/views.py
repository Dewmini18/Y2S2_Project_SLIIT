from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import F
from .models import NonMedicalProduct
from .forms import NonMedicalProductForm
import csv
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
import tempfile
import os
from django.utils import timezone
import base64
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import LoginView


def pharmacist_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == "pharmacist")(view_func)

@pharmacist_required
def product_list(request):
    """Display all non-medical products"""
    # Start with all products
    products = NonMedicalProduct.objects.all()
    
    # Get filter parameters from request
    category = request.GET.get('category')
    search_query = request.GET.get('search')
    
    # Apply filters
    if category:
        products = products.filter(category=category)
    
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Prepare context
    context = {
        'products': products,
        'categories': NonMedicalProduct.CATEGORY_CHOICES,
        'current_category': category,
        'search_query': search_query,
    }
    
    return render(request, 'Non_Medicine_inventory/product_list.html', context)

@pharmacist_required
def product_detail(request, slug):
    """Display details of a specific product"""
    product = get_object_or_404(NonMedicalProduct, slug=slug)
    context = {'product': product}
    return render(request, 'Non_Medicine_inventory/product_detail.html', context)

@pharmacist_required
def product_create(request):
    """Create a new non-medical product"""
    if request.method == 'POST':
        form = NonMedicalProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" has been created successfully.')
            return redirect('non_medicine:product_list')
    else:
        form = NonMedicalProductForm()
    
    context = {'form': form, 'title': 'Add New Product'}
    return render(request, 'Non_Medicine_inventory/product_form.html', context)

@pharmacist_required
def product_update(request, slug):
    """Update an existing non-medical product"""
    product = get_object_or_404(NonMedicalProduct, slug=slug)
    
    if request.method == 'POST':
        form = NonMedicalProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" has been updated successfully.')
            return redirect('non_medicine:product_detail', slug=product.slug)
    else:
        form = NonMedicalProductForm(instance=product)
    
    context = {'form': form, 'product': product, 'title': 'Update Product'}
    return render(request, 'Non_Medicine_inventory/product_form.html', context)

@pharmacist_required
def product_delete(request, slug):
    """Delete a non-medical product"""
    product = get_object_or_404(NonMedicalProduct, slug=slug)
    product_name = product.name
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, f'Product "{product_name}" has been deleted successfully.')
        return redirect('non_medicine:product_list')
    
    context = {'product': product}
    return render(request, 'Non_Medicine_inventory/product_confirm_delete.html', context)

@pharmacist_required
def product_table(request):
    """Display all non-medical products in a table format"""
    products = NonMedicalProduct.objects.all()
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    # Filter by search query if provided
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
        
    # Get unique categories for filter dropdown
    categories = NonMedicalProduct.CATEGORY_CHOICES
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category,
        'search_query': search_query,
    }
    return render(request, 'Non_Medicine_inventory/product_list_table.html', context)

@pharmacist_required
def export_pdf(request):
    # Get filtered products (same logic as in product_list view)
    products = NonMedicalProduct.objects.all()
    category = request.GET.get('category')
    search_query = request.GET.get('search')

    logo_file = os.path.join(settings.BASE_DIR, 'static/MediSyn_Logo/1.png')
    with open(logo_file, 'rb') as f:
        logo_data = base64.b64encode(f.read()).decode('utf-8')
    
    if category:
        products = products.filter(category=category)
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Prepare context for the template
    context = {
        'products': products,
        'title': 'Non-Medical Products Report',
        'now': timezone.now(),
        'logo_data': logo_data,
        'request': request,
    }
    
    # Render HTML content
    html_string = render_to_string('Non_Medicine_inventory/pdf_template.html', context)
    
    # Create HTTP response with PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="non_medical_products.pdf"'
    
    # Generate PDF from HTML
    HTML(string=html_string).write_pdf(response)
    
    return response

@pharmacist_required
def export_csv(request):
    # Get filtered products (same logic as in product_list view)
    products = NonMedicalProduct.objects.all()
    category = request.GET.get('category')
    search_query = request.GET.get('search')
    
    if category:
        products = products.filter(category=category)
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="non_medical_products.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Brand', 'Category', 'Description', 'Cost Price', 'Selling Price', 'Stock', 'Reorder Level', 'Status'])
    
    for product in products:
        writer.writerow([
            product.name,
            product.brand,
            product.get_category_display(),
            product.description,
            product.cost_price,
            product.selling_price,
            product.stock,
            product.reorder_level,
            'Active' if product.is_active else 'Inactive'
        ])
    
    return response