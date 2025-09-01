from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Medicine, MedicineAction
from .forms import MedicineForm
import csv
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from datetime import datetime
from django.db import IntegrityError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from Non_Medicine_inventory.models import NonMedicalProduct
from django.db.models import Count, F
import os
from django.conf import settings
from django.utils import timezone
import base64
from django.contrib.auth.decorators import login_required
from django.db.models import F
from Non_Medicine_inventory.models import NonMedicalProduct

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import LoginView


def pharmacist_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and u.role == "pharmacist")(view_func)


# View all medicines
@pharmacist_required
def view_medicine(request):
    medicines = Medicine.objects.all()
    categories = [c[0] for c in Medicine.CATEGORY_CHOICES]

    # Filtering
    category = request.GET.get('category')
    expiry = request.GET.get('expiry')
    low_stock = request.GET.get('low_stock')

    if category:
        medicines = medicines.filter(category=category)
    filtered = []
    for med in medicines:
        med.low_stock = med.quantity_in_stock < med.reorder_level
        med.near_expiry = med.is_near_expiry()
        med.is_expired = med.is_expired()
        if expiry == 'near' and not med.near_expiry:
            continue
        if expiry == 'expired' and not med.is_expired:
            continue
        if low_stock == 'low' and not med.low_stock:
            continue
        filtered.append(med)
    return render(request, 'Medicine_inventory/view_medicine.html', {
        'medicine': filtered,
        'categories': categories,
    })

@pharmacist_required
def view_medicine_cards(request):
    medicines = Medicine.objects.all()
    categories = [c[0] for c in Medicine.CATEGORY_CHOICES]

    # Filtering
    category = request.GET.get('category')
    expiry = request.GET.get('expiry')
    low_stock = request.GET.get('low_stock')

    if category:
        medicines = medicines.filter(category=category)
    filtered = []
    for med in medicines:
        med.low_stock = med.quantity_in_stock < med.reorder_level
        med.near_expiry = med.is_near_expiry()
        med.is_expired = med.is_expired()
        if expiry == 'near' and not med.near_expiry:
            continue
        if expiry == 'expired' and not med.is_expired:
            continue
        if low_stock == 'low' and not med.low_stock:
            continue
        filtered.append(med)

    recent_actions = MedicineAction.objects.select_related('medicine').order_by('-timestamp')[:5]
    return render(request, 'Medicine_inventory/view_medicine.html', {
        'medicine': filtered,
        'categories': categories,
        'recent_actions' : recent_actions,
    })

@pharmacist_required
def view_medicine_table(request):
    medicines = Medicine.objects.all()
    categories = [c[0] for c in Medicine.CATEGORY_CHOICES]

    # Sorting
    sort_by = request.GET.get('sort', 'name') # Default sort by name
    direction = request.GET.get('dir', 'asc') # Default direction ascending

    if sort_by not in ['name', 'quantity_in_stock']: # Whitelist sortable fields
        sort_by = 'name'

    order = sort_by if direction == 'asc' else f'-{sort_by}'
    medicines = medicines.order_by(order)

    # Filtering (applied after sorting)
    search_query = request.GET.get('search')
    category = request.GET.get('category')
    expiry = request.GET.get('expiry')
    low_stock = request.GET.get('low_stock')

    if search_query:
        medicines = medicines.filter(name__icontains=search_query)

    if category:
        medicines = medicines.filter(category=category)

    filtered = []
    for med in medicines:
        med.low_stock = med.quantity_in_stock < med.reorder_level
        med.near_expiry = med.is_near_expiry()
        med.is_expired = med.is_expired()
        
        # Expiry filter
        if expiry == 'near' and not med.near_expiry:
            continue
        if expiry == 'expired' and not med.is_expired:
            continue
        
        # Low stock filter
        if low_stock == 'low' and not med.low_stock:
            continue
        filtered.append(med)

    recent_actions = MedicineAction.objects.select_related('medicine').order_by('-timestamp')[:5]
    
    # Pass sorting info to the template
    context = {
        'medicine': filtered,
        'categories': categories,
        'recent_actions': recent_actions,
        'current_sort': sort_by,
        'current_dir': direction,
    }
    return render(request, 'Medicine_inventory/medicine_table.html', context)

# Create a new medicine entry
@pharmacist_required
def create_medicine(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)  # Include request.FILES
        if form.is_valid():
            medicine = form.save()
            # Add the user to the action record
            MedicineAction.objects.create(
                medicine=medicine,
                action='add',
                user=request.user  # Add this line
            )
            messages.success(request, f"Successfully registered new medication: '{medicine.name}'.")
            return redirect('medicine_table')
        else:
            form.add_error(None, "A medicine with this batch number already exists. Please change the batch details.")
    else:
        form = MedicineForm()
    return render(request, 'Medicine_inventory/create_medicine.html', {'form': form})

# Delete a medicine
@pharmacist_required
def delete_medicine(request, id):
    medicine = get_object_or_404(Medicine, pk=id)
    medicine_name = medicine.name
    
    MedicineAction.objects.create(
        medicine_name=medicine.name,
        batch_number=medicine.batch_number,
        action='delete',
        user=request.user  # Add this line
    )
    medicine.delete()
    
    messages.success(request, f"The record for '{medicine_name}' has been deleted successfully.")
    
    return redirect('medicine_table')

# Update a medicine
@pharmacist_required
def update_medicine(request, id):
    medicine = get_object_or_404(Medicine, pk=id)
    initial = {}
    if medicine.batch_number:
        parts = medicine.batch_number.split('-')
        if len(parts) == 4:
            initial = {
                'med_code': parts[0],
                'batch_date': str(parts[1]),
                'supplier_code': parts[2],
                'seq': parts[3],
            }
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)  # Include request.FILES
        if form.is_valid():
            medicine = form.save()
            MedicineAction.objects.create(
                medicine=medicine,
                action='update',
                user=request.user  # Add this line
            )
            
            messages.success(request, f"The record for '{medicine.name}' has been updated successfully.")
            
            return redirect('medicine_table')
    else:
        form = MedicineForm(instance=medicine, initial=initial)
    return render(request, 'Medicine_inventory/update_medicine.html', {'form': form, 'medicine': medicine})

# Home view
def home(request):
    return render(request, 'crudApp/home.html')

@pharmacist_required
def export_medicine_csv(request):
    medicines = Medicine.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="medicine_inventory.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Name', 'Brand', 'Category', 'Description', 'Dosage', 'Price',
        'Quantity In Stock', 'Reorder Level', 'Manufacture Date', 'Expiry Date',
        'Batch Number', 'Supplier'
    ])
    for med in medicines:
        writer.writerow([
            med.name, med.brand, med.category, med.description, med.dosage, med.selling_price, med.cost_price,
            med.quantity_in_stock, med.reorder_level, med.manufacture_date, med.expiry_date,
            med.batch_number, med.supplier
        ])
    return response

@pharmacist_required
def export_medicine_pdf(request):
    medicines = Medicine.objects.all()
    total_medicines = medicines.count()
    low_stock_count = Medicine.objects.filter(quantity_in_stock__lt=F('reorder_level')).count()
    expired = medicines.filter(expiry_date__lt=timezone.now().date()).count()

    logo_file = os.path.join(settings.BASE_DIR, 'static/MediSyn_Logo/1.png')
    with open(logo_file, 'rb') as f:
        logo_data = base64.b64encode(f.read()).decode('utf-8')

    context = {
        'medicines': medicines,
        'now': timezone.now(),
        'logo_data': logo_data,
        'total_medicines': total_medicines,
        'low_stock_count': low_stock_count,
        'expired': expired,
    }
    
    html_string = render_to_string('Medicine_inventory/medicine_pdf.html', context)
    pdf_file = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="medicine_inventory.pdf"'
    return response






@pharmacist_required
def med_inventory_dash(request):
    # Get medicine statistics
    total_medicines = Medicine.objects.count()
    
    # Use quantity_in_stock and reorder_level instead of low_stock
    low_stock_count = Medicine.objects.filter(quantity_in_stock__lt=F('reorder_level')).count()
    
    # Calculate near_expiry based on expiry_date
    today = timezone.now().date()
    expiry_threshold = today + timezone.timedelta(days=30)  # 30 days until expiry
    near_expiry_count = Medicine.objects.filter(
        expiry_date__gt=today,
        expiry_date__lte=expiry_threshold
    ).count()
    
    # Calculate expired based on expiry_date
    expired_count = Medicine.objects.filter(expiry_date__lt=today).count()
    
    # Get non-medical statistics
    total_nonmedical = NonMedicalProduct.objects.count()
    nonmedical_low_stock_count = NonMedicalProduct.objects.filter(stock__lt=F('reorder_level')).count()
    nonmedical_active_count = NonMedicalProduct.objects.filter(is_active=True).count()
    nonmedical_categories_count = NonMedicalProduct.objects.values('category').distinct().count()
    
    # Get chart data
    category_data = Medicine.objects.values('category').annotate(count=Count('id')).order_by('-count')
    category_labels = [item['category'] for item in category_data]
    category_counts = [item['count'] for item in category_data]
    
    # Get non-medical product category data
    nonmed_category_data = NonMedicalProduct.objects.values('category').annotate(count=Count('id')).order_by('-count')
    nonmed_category_labels = [item['category'] for item in nonmed_category_data]
    nonmed_category_counts = [item['count'] for item in nonmed_category_data]
    
    # Get recent medicines
    recent_medicines = Medicine.objects.all().order_by('-manufacture_date')[:5]
    
    # Get recent actions
    all_actions = MedicineAction.objects.all().order_by('-timestamp')
    paginator = Paginator(all_actions, 10)
    page = request.GET.get('page', 1)
    
    try:
        recent_actions = paginator.page(page)
    except PageNotAnInteger:
        recent_actions = paginator.page(1)
    except EmptyPage:
        recent_actions = paginator.page(paginator.num_pages)
    
    context = {
        'total_medicines': total_medicines,
        'low_stock_count': low_stock_count,
        'near_expiry_count': near_expiry_count,
        'expired_count': expired_count,
        'total_nonmedical': total_nonmedical,
        'nonmedical_low_stock_count': nonmedical_low_stock_count,
        'nonmedical_active_count': nonmedical_active_count,
        'nonmedical_categories_count': nonmedical_categories_count,
        'category_labels': category_labels,
        'category_counts': category_counts,
        'nonmed_category_labels': nonmed_category_labels,
        'nonmed_category_counts': nonmed_category_counts,
        'recent_medicines': recent_medicines,
        'recent_actions': recent_actions,
    }
    return render(request, 'Medicine_inventory/med_inventory_dash.html', context)



# Track recently viewed medicines
@pharmacist_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk)
    
    # Get recently viewed list from session (or empty list if not exists)
    recent_medicines = request.session.get('recent_medicines', [])
    
    # Remove this medicine if already in the list to avoid duplicates
    if pk in recent_medicines:
        recent_medicines.remove(pk)
    
    # Add current medicine to start of list and limit to 5 items
    recent_medicines.insert(0, pk)
    recent_medicines = recent_medicines[:5]
    
    # Save back to session
    request.session['recent_medicines'] = recent_medicines
    
    return render(request, 'Medicine_inventory/medicine_detail.html', {'medicine': medicine})

# Remember user's filter preferences
@pharmacist_required
def medicine_list(request):
    # Get filter parameters
    category = request.GET.get('category')
    sort_by = request.GET.get('sort')
    
    # If parameters provided, save to session
    if category:
        request.session['medicine_category_filter'] = category
    if sort_by:
        request.session['medicine_sort_by'] = sort_by
    
    # Use parameters from session if not provided in request
    if not category and 'medicine_category_filter' in request.session:
        category = request.session['medicine_category_filter']
    if not sort_by and 'medicine_sort_by' in request.session:
        sort_by = request.session['medicine_sort_by']
    
    # Apply filters to queryset
    medicines = Medicine.objects.all()
    if category and category != 'all':
        medicines = medicines.filter(category=category)
    
    if sort_by == 'name':
        medicines = medicines.order_by('name')
    elif sort_by == 'price_low':
        medicines = medicines.order_by('price')
    # Add other sorting options
    
    context = {
        'medicines': medicines,
        'current_category': category,
        'current_sort': sort_by,
    }
    
    return render(request, 'Medicine_inventory/medicine_list.html', context)

# Clear session filters
@pharmacist_required
def clear_filters(request):
    if 'medicine_category_filter' in request.session:
        del request.session['medicine_category_filter']
    if 'medicine_sort_by' in request.session:
        del request.session['medicine_sort_by']
    
    return redirect('medicine_list')

