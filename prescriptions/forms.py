# prescriptions/forms.py

from django import forms
from .models import Patient, Doctor, Prescription, PrescriptionItem, DrugInteraction
# Import the Medicine model from the Medicine_Inventory app
from Medicine_inventory.models import Medicine
from django.core.exceptions import ValidationError # Import ValidationError for custom validation

# Form for creating and updating Patient instances.
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        # Include all fields from the Patient model
        fields = '__all__'
        # Add widgets for better user experience, especially for date input
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Patient Last Name'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +1234567890'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Patient Address'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'patient@example.com'}),
        }
        # Labels for form fields
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'contact_number': 'Contact Number',
            'address': 'Address',
            'email' : 'Email-Address'
        }

# Form for creating and updating Doctor instances.
class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        # Include all fields from the Doctor model, now including medical_code
        fields = '__all__'
        # Add widgets for better user experience
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doctor First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Doctor Last Name'}),
            'specialization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., General Practitioner'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., +1234567890'}),
            'medical_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unique Medical Code (e.g., MD12345)'}),
        }
        # Labels for form fields
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'specialization': 'Specialization',
            'contact_number': 'Contact Number',
            'medical_code': 'Medical Code', # New label for the new field
        }

# Form for creating and updating Prescription instances.
# This form is now modified to verify doctor details by medical code.
class PrescriptionForm(forms.ModelForm):
    # These fields will be used for doctor verification.
    # They are not directly mapped to the Prescription model's fields.
    doctor_medical_code = forms.CharField(
        max_length=50,
        label="Doctor's Medical Code",
        help_text="Enter the unique medical code of the prescribing doctor.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., MD12345'})
    )
    doctor_last_name = forms.CharField(
        max_length=100,
        label="Doctor's Last Name",
        help_text="Enter the last name of the prescribing doctor for verification.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Smith'})
    )

    class Meta:
        model = Prescription
        # We now exclude 'doctor' from here, as it will be set after verification in clean() or form_valid().
        fields = ['patient', 'notes'] # Removed 'doctor'
        # Add widgets for better user experience
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Any additional notes for the prescription'}),
        }
        # Labels for form fields
        labels = {
            'patient': 'Select Patient',
            'notes': 'Prescription Notes',
        }

    # Custom validation for the entire form to verify doctor details.
    def clean(self):
        cleaned_data = super().clean()
        medical_code = cleaned_data.get('doctor_medical_code')
        last_name = cleaned_data.get('doctor_last_name')

        if medical_code and last_name:
            try:
                # Attempt to find a doctor matching both the medical code and last name.
                # Using __iexact for case-insensitive exact match for medical code.
                # Using __iexact for case-insensitive exact match for last name.
                doctor = Doctor.objects.get(
                    medical_code__iexact=medical_code,
                    last_name__iexact=last_name
                )
                # If a doctor is found, store the Doctor object in cleaned_data
                # so it can be accessed in the view (form_valid method).
                cleaned_data['doctor'] = doctor
            except Doctor.DoesNotExist:
                # If no matching doctor is found, raise a validation error.
                raise ValidationError(
                    "Invalid Doctor details. No registered doctor found with the provided Medical Code and Last Name. Please check the details or register the doctor.",
                    code='invalid_doctor'
                )
        elif not medical_code:
            # If medical code is missing, raise an error.
            self.add_error('doctor_medical_code', "Doctor's Medical Code is required.")
        elif not last_name:
            # If last name is missing, raise an error.
            self.add_error('doctor_last_name', "Doctor's Last Name is required.")

        return cleaned_data


# Form for creating and updating PrescriptionItem instances.
# This form is crucial for adding medicines to a prescription.
class PrescriptionItemForm(forms.ModelForm):
    # Override the medicine field to use a ModelChoiceField for better control
    # and to ensure it pulls from the Medicine_Inventory.Medicine model.
    # The queryset fetches all available medicines (batches) from the inventory.
    medicine = forms.ModelChoiceField(
        queryset=Medicine.objects.all().order_by('name', 'batch_number'),
        label="Select Medicine (Batch)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PrescriptionItem
        # We exclude 'prescription' as it will be set in the view based on the URL.
        # 'dispensed_quantity' will be handled by logic, not direct user input in this form.
        fields = ['medicine', 'dosage', 'duration', 'requested_quantity']
        # Add widgets for better user experience
        widgets = {
            'dosage': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 500mg, twice daily'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 7 days, until finished'}),
            'requested_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Quantity requested by patient'}),
        }
        # Labels for form fields
        labels = {
            'medicine': 'Medicine',
            'dosage': 'Dosage Instructions',
            'duration': 'Duration of Use',
            'requested_quantity': 'Requested Quantity',
        }

    # Custom validation for requested_quantity (optional, but good for early checks)
    def clean_requested_quantity(self):
        requested_quantity = self.cleaned_data['requested_quantity']
        if requested_quantity <= 0:
            raise forms.ValidationError("Requested quantity must be at least 1.")
        return requested_quantity

# Form for DrugInteraction (for future DL model population/management)
class DrugInteractionForm(forms.ModelForm):
    class Meta:
        model = DrugInteraction
        fields = '__all__'
        widgets = {
            'drug1_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Drug Name'}),
            'drug2_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Second Drug Name'}),
            'interaction_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description of the interaction'}),
            'severity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Mild, Moderate, Severe'}),
        }
        labels = {
            'drug1_name': 'Drug 1 Name',
            'drug2_name': 'Drug 2 Name',
            'interaction_description': 'Interaction Description',
            'severity': 'Severity',
        }

