# prescriptions/models.py
from django.db import models
from django.urls import reverse
from Medicine_inventory.models import Medicine
from datetime import date

# Model for patients.
# This model stores basic information about a patient.
class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True) 
    
    class Meta:
        # Orders patients by their last name, then first name, for consistent listing.
        ordering = ['last_name', 'first_name']

    def __str__(self):
        # String representation of the Patient object, useful for admin and debugging.
        return f"{self.first_name} {self.last_name}"

# Model for doctors.
# This model stores basic information about a doctor.
class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    medical_code = models.CharField(max_length=50, unique=True, help_text="Unique medical license or registration code")


    class Meta:
        # Orders doctors by their last name, then first name, for consistent listing.
        ordering = ['last_name', 'first_name']

    def __str__(self):
        # String representation of the Doctor object, including the new medical_code.
        return f"Dr. {self.first_name} {self.last_name} (Code: {self.medical_code})"

# Model for a prescription.
# This is the main prescription record, linking a patient and a doctor.
class Prescription(models.Model):
    # Date when the prescription was issued. Automatically set on creation.
    prescription_date = models.DateField(auto_now_add=True)
    # Foreign key to the Patient model. If a patient is deleted, their prescriptions are also deleted.
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    # Foreign key to the Doctor model. If a doctor is deleted, their prescriptions are also deleted.
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='prescriptions')
    # Optional notes for the prescription, e.g., general instructions.
    notes = models.TextField(blank=True, null=True)
    # Field to indicate if the prescription has been validated for drug interactions.
    # Default is False. This will be updated by the Deep Learning model later.
    is_validated = models.BooleanField(default=False)
    # Field to store potential interaction warnings from the Deep Learning model.
    # This will be populated if drug interactions are detected.
    interaction_warning = models.TextField(blank=True, null=True)
    # New field to track if the prescription has been paid for.
    is_paid = models.BooleanField(default=False)

    class Meta:
        # Orders prescriptions by date in descending order (most recent first).
        ordering = ['-prescription_date']

    def __str__(self):
        # String representation of the Prescription object.
        return f"Prescription #{self.id} for {self.patient} by {self.doctor} on {self.prescription_date}"

    def get_absolute_url(self):
        # Returns the URL to access a particular instance of the Prescription.
        # This is useful for redirects after creating/updating an object.
        return reverse('prescription_detail', kwargs={'pk': self.pk})

    @property
    def total_cost(self):
        """
        Calculates the total cost of the prescription by summing up the total
        price of each associated PrescriptionItem.
        """
        return sum(item.total_price for item in self.items.all())


# Model for individual medicine items within a prescription.
# This links a specific medicine (batch) from the inventory to a prescription.
class PrescriptionItem(models.Model):
    # Foreign key to the Prescription model. If a Prescription is deleted, its items are also deleted.
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    # Foreign key to the Medicine model from Medicine_Inventory app.
    # This links to a specific batch of medicine.
    # on_delete=models.PROTECT prevents deleting a Medicine if it's part of an existing prescription.
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='prescription_items')
    # The dosage instructions for this medicine in this prescription (e.g., "1 tablet, twice daily").
    dosage = models.CharField(max_length=100)
    # The duration for which the medicine should be taken (e.g., "7 days", "until finished").
    duration = models.CharField(max_length=100)
    # The quantity of this specific medicine (batch) requested by the patient/pharmacist.
    requested_quantity = models.PositiveIntegerField()
    # The actual quantity of this specific medicine (batch) dispensed to the patient.
    # This is the quantity that will affect the inventory.
    dispensed_quantity = models.PositiveIntegerField(default=0)


    class Meta:
        # Ensures that a specific medicine (batch) can only be added once to a given prescription.
        # This prevents duplicate entries for the same medicine within the same prescription.
        unique_together = ('prescription', 'medicine')

    def __str__(self):
        # String representation of the PrescriptionItem object.
        return f"{self.medicine.name} ({self.dispensed_quantity} units) for Prescription #{self.prescription.id}"

    @property
    def price_per_unit(self):
        """Gets the selling price of the medicine from the linked Medicine model."""
        return self.medicine.selling_price

    @property
    def total_price(self):
        """Calculates the total price for this item based on dispensed quantity and selling price."""
        return self.dispensed_quantity * self.price_per_unit

# Model for storing known drug interactions.
# This table will be populated and used by the Deep Learning model (Option A).
# It will serve as a lookup for detected interactions.
class DrugInteraction(models.Model):
    # The name of the first medicine involved in the interaction.
    drug1_name = models.CharField(max_length=255)
    # The name of the second medicine involved in the interaction.
    drug2_name = models.CharField(max_length=255)
    # Description of the harmful interaction (e.g., "May cause severe drowsiness").
    interaction_description = models.TextField()
    # Severity of the interaction (e.g., 'Mild', 'Moderate', 'Severe').
    severity = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        # Ensures unique interactions, regardless of the order of drug names.
        # (Drug A + Drug B is considered the same as Drug B + Drug A).
        unique_together = (('drug1_name', 'drug2_name'), ('drug2_name', 'drug1_name'))
        # Orders interactions by severity for easier review.
        ordering = ['severity']

    def __str__(self):
        # String representation of the DrugInteraction object.
        return f"Interaction: {self.drug1_name} + {self.drug2_name} ({self.severity})"
