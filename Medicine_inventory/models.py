from django.db import models
from datetime import date, timedelta
from django.conf import settings


class Medicine(models.Model):
    CATEGORY_CHOICES = [
    ('Analgesic', 'Analgesic'),               # Pain relief
    ('Antibiotic', 'Antibiotic'),             # Bacterial infections
    ('Antiviral', 'Antiviral'),               # Viral infections
    ('Antifungal', 'Antifungal'),             # Fungal infections
    ('Antihistamine', 'Antihistamine'),       # Allergy relief
    ('Antacid', 'Antacid'),                   # Acid reflux, ulcers
    ('Antipyretic', 'Antipyretic'),           # Fever reducers
    ('Anti-inflammatory', 'Anti-inflammatory'),# Inflammation reduction
    ('Antihypertensive', 'Antihypertensive'), # Blood pressure
    ('Antidiabetic', 'Antidiabetic'),         # Blood sugar control
    ('Antidepressant', 'Antidepressant'),     # Mood disorders
    ('Anticoagulant', 'Anticoagulant'),       # Blood thinners
    ('Diuretic', 'Diuretic'),                 # Fluid removal
    ('Sedative', 'Sedative'),                 # Anxiety, sleep aid
    ('Bronchodilator', 'Bronchodilator'),     # Asthma/COPD
    ('Vaccine', 'Vaccine'),                   # Immunization
    ('Steroid', 'Steroid'),                   # Corticosteroids
    ('Contraceptive', 'Contraceptive'),       # Birth control
    ('Antiemetic', 'Antiemetic'),             # Nausea/vomiting
    ('Antipsychotic', 'Antipsychotic'),       # Mental illness
    ('Muscle Relaxant', 'Muscle Relaxant'),   # Muscle spasms
    ('Chemotherapy', 'Chemotherapy'),         # Cancer treatment
    ('Immunosuppressant', 'Immunosuppressant'),# Transplant, autoimmune
    ('Ophthalmic', 'Ophthalmic'),             # Eye treatments
    ('Dermatological', 'Dermatological'),     # Skin applications
    ('Nutritional Supplement', 'Nutritional Supplement'), # Vitamins
    ('Respiratory Agent', 'Respiratory Agent'),# Cough, congestion
    ('Local Anesthetic', 'Local Anesthetic'), # Numbing agents
    ]

    MEDICINE_TYPE_CHOICES = [
        ('RX', 'RX'),
        ('OTC', 'OTC'),
    ]

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    medicine_type = models.CharField(
        max_length=10,
        choices=MEDICINE_TYPE_CHOICES,
        default='RX'
    )
    description = models.TextField(blank=True)
    dosage = models.CharField(max_length=50)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='medical_products/', blank=True, null=True)
    quantity_in_stock = models.PositiveIntegerField()
    reorder_level = models.PositiveIntegerField(default=10)
    manufacture_date = models.DateField()
    expiry_date = models.DateField()
    batch_number = models.CharField(max_length=150, unique=True)
    supplier = models.CharField(max_length=100)

    def is_expired(self):
        return date.today() >= self.expiry_date

    def is_near_expiry(self):
        return (
            self.expiry_date
            and date.today() < self.expiry_date
            and (self.expiry_date - date.today()) <= timedelta(days=7)
        )

    def __str__(self):
        return f"{self.name} - {self.dosage} ({self.batch_number})"

class MedicineAction(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
    ]
    medicine = models.ForeignKey(Medicine, on_delete=models.SET_NULL, null=True, blank=True)
    medicine_name = models.CharField(max_length=255, blank=True, null=True)
    batch_number = models.CharField(max_length=255, blank=True, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.medicine.name} {self.get_action_display()} at {self.timestamp}"