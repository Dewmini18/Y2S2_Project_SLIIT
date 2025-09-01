# prescriptions/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db import transaction # Used for atomic operations (e.g., stock management)
from django.contrib import messages # For displaying user feedback messages
from django.http import HttpResponse
from django.db.models.deletion import ProtectedError
# Import models and forms from your prescriptions app
from .models import Patient, Doctor, Prescription, PrescriptionItem, DrugInteraction
from .forms import PatientForm, DoctorForm, PrescriptionForm, PrescriptionItemForm

# Import the Medicine model from the Medicine_Inventory app
from Medicine_inventory.models import Medicine

# For PDF generation
from weasyprint import HTML
import io


# --- Patient CRUD Views ---
# These views handle the creation, listing, updating, and deleting of Patient records.
# While not directly part of Prescription CRUD, they are necessary for selecting patients.

class PatientListView(ListView):
    # Specifies the model this view will operate on.
    model = Patient
    # Specifies the template to use for rendering the list of patients.
    template_name = 'prescriptions/patient_list.html'
    # The context object name used in the template (e.g., 'object_list' becomes 'patients').
    context_object_name = 'patients'
    # Enables pagination for the list view, showing 10 patients per page.
    paginate_by = 10

    def get_queryset(self):
        # Allows filtering of patients based on search queries.
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            # Filters patients whose first name or last name contains the query string (case-insensitive).
            queryset = queryset.filter(first_name__icontains=query) | \
                       queryset.filter(last_name__icontains=query)
        return queryset

class PatientCreateView(CreateView):
    # Specifies the model for creating new patient instances.
    model = Patient
    # Specifies the form to use for creating a patient.
    form_class = PatientForm
    # Specifies the template for the patient creation form.
    template_name = 'prescriptions/patient_form.html'
    # URL to redirect to after successful patient creation.
    success_url = reverse_lazy('patient_list')

    def form_valid(self, form):
        # Called if the form is valid. Saves the new patient and displays a success message.
        messages.success(self.request, "Patient created successfully!")
        return super().form_valid(form)

class PatientDetailView(DetailView):
    # Specifies the model for viewing patient details.
    model = Patient
    # Specifies the template for displaying patient details.
    template_name = 'prescriptions/patient_detail.html'
    # The context object name used in the template.
    context_object_name = 'patient'

class PatientUpdateView(UpdateView):
    # Specifies the model for updating patient instances.
    model = Patient
    # Specifies the form to use for updating a patient.
    form_class = PatientForm
    # Specifies the template for the patient update form.
    template_name = 'prescriptions/patient_form.html'
    # URL to redirect to after successful patient update.
    success_url = reverse_lazy('patient_list')

    def form_valid(self, form):
        # Called if the form is valid. Updates the patient and displays a success message.
        messages.success(self.request, "Patient updated successfully!")
        return super().form_valid(form)

class PatientDeleteView(DeleteView):
    # Specifies the model for deleting patient instances.
    model = Patient
    # Specifies the template for confirming patient deletion.
    template_name = 'prescriptions/patient_confirm_delete.html'
    # URL to redirect to after successful patient deletion.
    success_url = reverse_lazy('patient_list')

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "This patient cannot be deleted because they are associated with an existing prescription.")
            return redirect('patient_list')
    

# --- Doctor CRUD Views ---
# These views handle the creation, listing, updating, and deleting of Doctor records.
# Necessary for selecting doctors for prescriptions.

class DoctorListView(ListView):
    model = Doctor
    template_name = 'prescriptions/doctor_list.html'
    context_object_name = 'doctors'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(first_name__icontains=query) | \
                       queryset.filter(last_name__icontains=query) | \
                       queryset.filter(specialization__icontains=query) | \
                       queryset.filter(medical_code__icontains=query) # Added search by medical_code
        return queryset

class DoctorCreateView(CreateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'prescriptions/doctor_form.html'
    success_url = reverse_lazy('doctor_list')

    def form_valid(self, form):
        messages.success(self.request, "Doctor created successfully!")
        return super().form_valid(form)

class DoctorDetailView(DetailView):
    model = Doctor
    template_name = 'prescriptions/doctor_detail.html'
    context_object_name = 'doctor'

class DoctorUpdateView(UpdateView):
    model = Doctor
    form_class = DoctorForm
    template_name = 'prescriptions/doctor_form.html'
    success_url = reverse_lazy('doctor_list')

    def form_valid(self, form):
        messages.success(self.request, "Doctor updated successfully!")
        return super().form_valid(form)

class DoctorDeleteView(DeleteView):
    model = Doctor
    template_name = 'prescriptions/doctor_confirm_delete.html'
    success_url = reverse_lazy('doctor_list')

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, "This doctor cannot be deleted because they are associated with an existing prescription.")
            return redirect('doctor_list')


# --- Prescription CRUD Views ---
# These are the core views for managing prescriptions.

class PrescriptionListView(ListView):
    model = Prescription
    template_name = 'prescriptions/prescription_list.html'
    context_object_name = 'prescriptions'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtering by patient, doctor, date
        patient_query = self.request.GET.get('patient')
        doctor_query = self.request.GET.get('doctor')
        date_query = self.request.GET.get('date')

        if patient_query:
            queryset = queryset.filter(patient__id=patient_query)
        if doctor_query:
            queryset = queryset.filter(doctor__id=doctor_query)
        if date_query:
            queryset = queryset.filter(prescription_date=date_query)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add lists of patients and doctors to the context for filter dropdowns
        context['patients'] = Patient.objects.all().order_by('first_name')
        context['doctors'] = Doctor.objects.all().order_by('first_name')
        return context


class PrescriptionCreateView(CreateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'prescriptions/prescription_form.html'
    # We will redirect to the detail view of the newly created prescription
    # to allow adding PrescriptionItems immediately.
    # The success_url is a method because we need the PK of the new object.
    def get_success_url(self):
        return reverse_lazy('prescription_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        # The 'doctor' object is now available in form.cleaned_data due to custom validation in PrescriptionForm.
        form.instance.doctor = form.cleaned_data['doctor']
        response = super().form_valid(form)
        messages.success(self.request, "Prescription created successfully! Now add medicines.")
        return response


class PrescriptionDetailView(DetailView):
    model = Prescription
    template_name = 'prescriptions/prescription_detail.html'
    context_object_name = 'prescription'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all PrescriptionItems related to this prescription
        context['prescription_items'] = self.object.items.all()
        # Form for adding new prescription items (will be displayed on the detail page)
        context['form'] = PrescriptionItemForm()
        # All medicines for the dropdown in the PrescriptionItemForm
        context['all_medicines'] = Medicine.objects.all().order_by('name', 'batch_number')
        
        # Check if there's a confirmation needed from a previous attempt to add an item
        if 'confirm_needed' in self.request.session:
            confirm_data = self.request.session.pop('confirm_needed') # Get and remove from session
            context.update(confirm_data) # Add confirmation data to context
        
        # ADDED: Add the total cost to the context for display
        context['total_cost'] = self.object.total_cost
        
        return context


# --- PrescriptionItem Views (for adding/updating/deleting items within a Prescription) ---
# These are function-based views for more granular control over stock management.

def add_prescription_item(request, pk):
    # Get the parent prescription or return a 404 if not found.
    prescription = get_object_or_404(Prescription, pk=pk)
    if request.method == 'POST':
        form = PrescriptionItemForm(request.POST)
        
        # Check for confirmation flag from the modal
        confirm_dispense = request.POST.get('confirm_dispense') == 'true'
        
        if form.is_valid():
            medicine_selected = form.cleaned_data['medicine']
            requested_quantity = form.cleaned_data['requested_quantity']

            with transaction.atomic():
                medicine_in_stock = Medicine.objects.select_for_update().get(pk=medicine_selected.pk)

                if requested_quantity > medicine_in_stock.quantity_in_stock:
                    # Insufficient stock, confirmation needed
                    if not confirm_dispense:
                        # Store data in session and redirect to detail page to show modal
                        request.session['confirm_needed'] = {
                            'confirm_needed': True,
                            'medicine_name': medicine_in_stock.name,
                            'medicine_batch': medicine_in_stock.batch_number,
                            'available_quantity': medicine_in_stock.quantity_in_stock,
                            'requested_quantity_initial': requested_quantity, # Store initial requested
                            'form_data': request.POST.dict() # Store all form data for re-submission
                        }
                        messages.warning(request, f"Insufficient stock for {medicine_in_stock.name} (Batch: {medicine_in_stock.batch_number}). Only {medicine_in_stock.quantity_in_stock} available. Please confirm to dispense available quantity.")
                        return redirect('prescription_detail', pk=prescription.pk)
                    else:
                        # Pharmacist confirmed to dispense available quantity
                        dispensed_quantity = medicine_in_stock.quantity_in_stock
                        messages.success(request, f"Dispensing available {dispensed_quantity} units of {medicine_in_stock.name} (Batch: {medicine_in_stock.batch_number}). Stock updated.")
                else:
                    # Sufficient stock, dispense requested quantity
                    dispensed_quantity = requested_quantity
                    messages.success(request, f"Added {dispensed_quantity} units of {medicine_in_stock.name} to prescription. Stock updated.")

                if dispensed_quantity > 0:
                    existing_item = PrescriptionItem.objects.filter(
                        prescription=prescription,
                        medicine=medicine_in_stock
                    ).first()

                    if existing_item:
                        # If item already exists, update its quantity
                        # When updating, we need to consider the difference from the original dispensed quantity
                        # to correctly adjust stock. This logic is getting complex, so for simplicity
                        # in the confirmation flow, we'll just add the newly dispensed amount.
                        # For a robust update, you'd need to calculate the delta (new_dispensed - old_dispensed)
                        # and adjust stock by that delta. For now, this is an 'add new' flow.
                        existing_item.requested_quantity += requested_quantity # Update requested
                        existing_item.dispensed_quantity += dispensed_quantity # Add newly dispensed to existing
                        existing_item.dosage = form.cleaned_data['dosage']
                        existing_item.duration = form.cleaned_data['duration']
                        existing_item.save()
                        messages.info(request, f"Updated existing item for {medicine_in_stock.name} in prescription.")
                    else:
                        prescription_item = form.save(commit=False)
                        prescription_item.prescription = prescription
                        prescription_item.dispensed_quantity = dispensed_quantity
                        prescription_item.save()

                    medicine_in_stock.quantity_in_stock -= dispensed_quantity
                    medicine_in_stock.save()

                    prescription.is_validated = False
                    prescription.interaction_warning = None
                    prescription.save()

                    return redirect('prescription_detail', pk=prescription.pk)
                else:
                    # This case happens if requested_quantity > available_stock, and available_stock is 0.
                    # The message is already set above.
                    return redirect('prescription_detail', pk=prescription.pk)
        else:
            messages.error(request, "Error adding medicine to prescription. Please check your input.")
            context = {
                'prescription': prescription,
                'prescription_items': prescription.items.all(),
                'form': form,
                'all_medicines': Medicine.objects.all().order_by('name', 'batch_number')
            }
            return render(request, 'prescriptions/prescription_detail.html', context)
    return redirect('prescription_detail', pk=prescription.pk)


def update_prescription_item(request, pk, item_pk):
    # Get the parent prescription and the specific item.
    prescription = get_object_or_404(Prescription, pk=pk)
    prescription_item = get_object_or_404(PrescriptionItem, pk=item_pk, prescription=prescription)

    if request.method == 'POST':
        # Create a form instance with the POST data and the existing item instance.
        # We need to exclude 'prescription' and 'dispensed_quantity' from the form's fields
        # if we want to manually handle them.
        form = PrescriptionItemForm(request.POST, instance=prescription_item)
        if form.is_valid():
            # Get the original dispensed quantity before update.
            original_dispensed_quantity = prescription_item.dispensed_quantity
            medicine_selected = form.cleaned_data['medicine']
            new_requested_quantity = form.cleaned_data['requested_quantity']

            with transaction.atomic():
                # Lock the medicine row for update to prevent race conditions.
                medicine_in_stock = Medicine.objects.select_for_update().get(pk=medicine_selected.pk)

                # Calculate the change in quantity needed from stock.
                # If new_requested_quantity is less than original, stock is returned.
                # If new_requested_quantity is more than original, stock is taken.
                quantity_difference = new_requested_quantity - original_dispensed_quantity

                if quantity_difference > 0: # More quantity requested
                    if quantity_difference <= medicine_in_stock.quantity_in_stock:
                        new_dispensed_quantity = original_dispensed_quantity + quantity_difference
                        medicine_in_stock.quantity_in_stock -= quantity_difference
                        messages.success(request, f"Updated {medicine_in_stock.name} quantity. Stock decreased.")
                    else:
                        # Not enough stock for the full increase.
                        # Dispense up to available stock.
                        actual_increase = medicine_in_stock.quantity_in_stock
                        new_dispensed_quantity = original_dispensed_quantity + actual_increase
                        medicine_in_stock.quantity_in_stock -= actual_increase
                        messages.warning(request, f"Only {actual_increase} more units of {medicine_in_stock.name} (batch {medicine_in_stock.batch_number}) available. Dispensing up to total {new_dispensed_quantity}.")
                else: # Quantity decreased or no change
                    new_dispensed_quantity = new_requested_quantity # Assume requested = dispensed for decrease
                    # Return the difference (absolute value) to stock.
                    medicine_in_stock.quantity_in_stock += abs(quantity_difference)
                    messages.success(request, f"Updated {medicine_in_stock.name} quantity. Stock increased.")

                # Update the PrescriptionItem with the new quantities.
                prescription_item.requested_quantity = new_requested_quantity
                prescription_item.dispensed_quantity = new_dispensed_quantity
                prescription_item.dosage = form.cleaned_data['dosage']
                prescription_item.duration = form.cleaned_data['duration']
                prescription_item.medicine = medicine_selected # In case medicine itself was changed
                prescription_item.save()
                medicine_in_stock.save() # Save the updated medicine stock

                # --- Drug Interaction Re-validation (Future Integration Point) ---
                prescription.is_validated = False # Mark as needing re-validation
                prescription.interaction_warning = None # Clear old warnings
                prescription.save() # Save the prescription to update its validation status

                messages.success(request, "Prescription item updated successfully.")
                return redirect('prescription_detail', pk=prescription.pk)
        else:
            messages.error(request, "Error updating prescription item. Please check your input.")
            # If form invalid, re-render the detail page with errors.
            context = {
                'prescription': prescription,
                'prescription_items': prescription.items.all(),
                'form': form, # Pass the form with errors back
                'all_medicines': Medicine.objects.all().order_by('name', 'batch_number'),
                'item_to_edit': prescription_item # To pre-fill the edit form
            }
            return render(request, 'prescriptions/prescription_detail.html', context)
    else:
        # For GET request, pre-fill the form with existing item data.
        form = PrescriptionItemForm(instance=prescription_item)
        context = {
            'prescription': prescription,
            'prescription_items': prescription.items.all(),
            'form': form,
            'all_medicines': Medicine.objects.all().order_by('name', 'batch_number'),
            'item_to_edit': prescription_item # To pre-fill the edit form
        }
        return render(request, 'prescriptions/prescription_detail.html', context)


def delete_prescription_item(request, pk, item_pk):
    # Get the parent prescription and the specific item.
    prescription = get_object_or_404(Prescription, pk=pk)
    prescription_item = get_object_or_404(PrescriptionItem, pk=item_pk, prescription=prescription)

    if request.method == 'POST':
        with transaction.atomic():
            # Before deleting, return the dispensed quantity to stock.
            medicine_in_stock = Medicine.objects.select_for_update().get(pk=prescription_item.medicine.pk)
            medicine_in_stock.quantity_in_stock += prescription_item.dispensed_quantity
            medicine_in_stock.save()

            # Delete the prescription item.
            prescription_item.delete()

            # --- Drug Interaction Re-validation (Future Integration Point) ---
            prescription.is_validated = False # Mark as needing re-validation
            prescription.interaction_warning = None # Clear old warnings
            prescription.save() # Save the prescription to update its validation status

            messages.success(request, f"Medicine '{prescription_item.medicine.name}' removed from prescription and stock returned.")
        return redirect('prescription_detail', pk=prescription.pk)
    # For GET request, show a confirmation page (optional, but good practice)
    return render(request, 'prescriptions/prescription_item_confirm_delete.html', {
        'prescription_item': prescription_item,
        'prescription': prescription
    })


class PrescriptionUpdateView(UpdateView):
    model = Prescription
    form_class = PrescriptionForm
    template_name = 'prescriptions/prescription_form.html'
    success_url = reverse_lazy('prescription_list') # Redirect to list after main prescription update

    def form_valid(self, form):
        # The 'doctor' object is now available in form.cleaned_data due to custom validation in PrescriptionForm.
        form.instance.doctor = form.cleaned_data['doctor']
        # When main prescription details are updated, re-evaluate interactions if needed.
        # For now, just mark for re-validation.
        form.instance.is_validated = False
        form.instance.interaction_warning = None
        messages.success(self.request, "Prescription details updated successfully!")
        return super().form_valid(form)


class PrescriptionDeleteView(DeleteView):
    model = Prescription
    template_name = 'prescriptions/prescription_confirm_delete.html'
    success_url = reverse_lazy('prescription_list')

    def form_valid(self, form):
        try:
            self.object.delete()
            messages.success(self.request, "Prescription was successfully deleted.")
            return redirect(self.success_url)
        except ProtectedError:
            messages.error(self.request, "This prescription cannot be deleted because it has a related payment. Please cancel the payment instead.")
            return redirect('prescription_detail', pk=self.object.pk)


# ADDED: A new function-based view to mark a prescription as paid.
def mark_prescription_as_paid(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)

    # We only want to handle POST requests to update the payment status.
    if request.method == 'POST':
        with transaction.atomic():
            prescription.is_paid = True
            prescription.save()
        messages.success(request, f"Prescription #{prescription.id} has been marked as paid.")
    else:
        messages.error(request, "Invalid request method.")
    
    return redirect('prescription_detail', pk=prescription.pk)


# --- PDF Generation View ---
# This view generates a PDF of the prescription details.

def generate_prescription_pdf(request, pk):
    # ADDED: Get the prescription and its items with a single query for efficiency
    prescription = get_object_or_404(Prescription.objects.prefetch_related('items__medicine'), pk=pk)

    # Create a file-like buffer to receive PDF data.
    buffer = io.BytesIO()

    # Generate table rows first
    table_rows = "".join([
        f"""
        <tr>
            <td>{item.medicine.name} ({item.medicine.batch_number})</td>
            <td>{item.dosage}</td>
            <td class="quantity-cell">{item.dispensed_quantity}</td>
            <td>{item.medicine.description or 'N/A'}</td>
            <td class="quantity-cell">${item.total_price:.2f}</td>
        </tr>
        """ for item in prescription.items.all()
    ])

    # Prepare the notes section separately
    notes_section_html = ""
    if prescription.notes:
        notes_section_html = f"""
        <div class="notes-section">
            <h3>Notes:</h3>
            <p>{prescription.notes}</p>
        </div>
        """
    
    # ADDED: Determine payment status string
    payment_status = "Paid" if prescription.is_paid else "Unpaid"

    # Construct the HTML content for the PDF
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Prescription #{prescription.id}</title>
        <style>
            body {{ font-family: sans-serif; margin: 0.75in; font-size: 10pt; }}
            .header {{ text-align: center; margin-bottom: 20pt; }}
            .header h1 {{ font-size: 24pt; margin-bottom: 5pt; color: #1a202c; }}
            .header p {{ font-size: 9pt; color: #4a5568; }}
            .line {{ border-bottom: 1pt solid #cbd5e0; margin-top: 20pt; margin-bottom: 30pt; }}
            .section-title {{ font-size: 14pt; font-weight: bold; text-align: center; margin-bottom: 20pt; color: #2d3748; }}
            .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; margin-bottom: 20pt; }}
            .info-item {{ margin-bottom: 5pt; }}
            .info-item strong {{ font-weight: bold; color: #2d3748; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20pt; }}
            th, td {{ border: 1pt solid #e2e8f0; padding: 8pt; text-align: left; vertical-align: middle; }}
            th {{ background-color: #f7fafc; font-weight: bold; text-align: center; color: #2d3748; }}
            .quantity-cell {{ text-align: center; }}
            .notes-section {{ margin-top: 30pt; }}
            .notes-section h3 {{ font-size: 12pt; font-weight: bold; margin-bottom: 10pt; color: #2d3748; }}
            .footer {{ text-align: center; margin-top: 40pt; font-size: 10pt; color: #4a5568; }}
            .footer strong {{ font-weight: bold; }}
            .total-cost {{ font-size: 12pt; font-weight: bold; text-align: right; margin-top: 10pt; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Your Pharmacy Name</h1>
            <p>123 Pharmacy Lane, City, Country | Phone: (123) 456-7890</p>
        </div>
        <div class="line"></div>

        <h2 class="section-title">Prescription Details</h2>

        <div class="info-grid">
            <div class="info-item">
                <strong>Prescription ID:</strong> {prescription.id}
            </div>
            <div class="info-item">
                <strong>Date:</strong> {prescription.prescription_date.strftime('%Y-%m-%d')}
            </div>
            <div class="info-item">
                <strong>Patient:</strong> {prescription.patient.first_name} {prescription.patient.last_name} (DOB: {prescription.patient.date_of_birth.strftime('%Y-%m-%d')})
            </div>
            <div class="info-item">
                <strong>Doctor:</strong> Dr. {prescription.doctor.first_name} {prescription.doctor.last_name} (Code: {prescription.doctor.medical_code}) ({prescription.doctor.specialization or 'N/A'})
            </div>
            <div class="info-item">
                <strong>Payment Status:</strong> {payment_status}
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Medicine Name</th>
                    <th>Dosage</th>
                    <th class="quantity-cell">Quantity</th>
                    <th>Description</th>
                    <th class="quantity-cell">Price</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
        
        <div class="total-cost">
            Total Cost: ${prescription.total_cost:.2f}
        </div>

        {notes_section_html}

        <div class="footer">
            <p>Please present this PDF at the billing counter for payment.</p>
            <p><strong>Thank you for choosing our pharmacy!</strong></p>
        </div>
    </body>
    </html>
    """

    # Generate PDF from HTML content using WeasyPrint
    HTML(string=html_content).write_pdf(buffer)

    # Get the value of the BytesIO buffer and set up the HTTP response.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="prescription_{prescription.id}.pdf"'
    return response

