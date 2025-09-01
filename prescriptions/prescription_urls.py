# prescriptions/prescription_urls.py

from django.urls import path
from . import views # Import all views from the current app

urlpatterns = [
    # --- Patient URLs ---
    # List all patients
    path('patients/', views.PatientListView.as_view(), name='patient_list'),
    # Create a new patient
    path('patients/add/', views.PatientCreateView.as_view(), name='patient_create'),
    # View details of a specific patient
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name='patient_detail'),
    # Update a specific patient
    path('patients/<int:pk>/edit/', views.PatientUpdateView.as_view(), name='patient_update'),
    # Delete a specific patient
    path('patients/<int:pk>/delete/', views.PatientDeleteView.as_view(), name='patient_delete'),

    # --- Doctor URLs ---
    # List all doctors
    path('doctors/', views.DoctorListView.as_view(), name='doctor_list'),
    # Create a new doctor
    path('doctors/add/', views.DoctorCreateView.as_view(), name='doctor_create'),
    # View details of a specific doctor
    path('doctors/<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),
    # Update a specific doctor
    path('doctors/<int:pk>/edit/', views.DoctorUpdateView.as_view(), name='doctor_update'),
    # Delete a specific doctor
    path('doctors/<int:pk>/delete/', views.DoctorDeleteView.as_view(), name='doctor_delete'),

    # --- Prescription URLs ---
    # List all prescriptions
    path('prescription/', views.PrescriptionListView.as_view(), name='prescription_list'),
    # Create a new prescription
    path('prescription/add/', views.PrescriptionCreateView.as_view(), name='prescription_create'),
    # View details of a specific prescription
    path('prescription/<int:pk>/', views.PrescriptionDetailView.as_view(), name='prescription_detail'),
    # Update a specific prescription
    path('prescription/<int:pk>/edit/', views.PrescriptionUpdateView.as_view(), name='prescription_update'),
    # Delete a specific prescription
    path('prescription/<int:pk>/delete/', views.PrescriptionDeleteView.as_view(), name='prescription_delete'),

    # --- PrescriptionItem URLs (nested under Prescription detail) ---
    # Add a medicine item to a specific prescription
    path('prescription/<int:pk>/items/add/', views.add_prescription_item, name='add_prescription_item'),
    # Update a specific medicine item within a prescription
    path('prescription/<int:pk>/items/<int:item_pk>/edit/', views.update_prescription_item, name='update_prescription_item'),
    # Delete a specific medicine item from a prescription
    path('prescription/<int:pk>/items/<int:item_pk>/delete/', views.delete_prescription_item, name='delete_prescription_item'),

    # --- PDF Generation URL ---
    # Generate PDF for a specific prescription
    path('prescription/<int:pk>/pdf/', views.generate_prescription_pdf, name='generate_prescription_pdf'),
    path('prescription/<int:pk>/mark_paid/', views.mark_prescription_as_paid, name='mark_prescription_as_paid'),
    
    # --- DrugInteraction URLs (for future admin/management, optional for now) ---
    # You might add views for DrugInteraction later if needed for non-admin CRUD.
    # For now, it's primarily managed via Django Admin or by the DL model.
]
