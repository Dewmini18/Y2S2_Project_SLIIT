from django.db import models
from django.db.models import Sum
from prescriptions.models import *

class Payment(models.Model):
    
    # Link to the patient who is paying for the prescription.
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, related_name='payments')
    
    # Link to the specific prescription being paid for.
    # on_delete=models.PROTECT prevents a prescription from being deleted if a payment exists for it.
    prescription = models.ForeignKey(Prescription, on_delete=models.PROTECT, related_name='payments')
    
    # Total amount of the payment. This is calculated dynamically.
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Status of the payment (e.g., 'pending', 'paid', 'cancelled').
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamp for when the payment was created.
    payment_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        # Change this line
        return f"Invoice #{self.id} for {self.patient.first_name} {self.patient.last_name} ({self.status})"
        # It's better to use first_name and last_name directly
        
    def calculate_total(self):
        total = self.payment_items.aggregate(total=Sum('total_price'))['total']
        self.total_amount = total if total is not None else 0.00
        self.save()

class PaymentItem(models.Model):
    # Link to the Payment object this item belongs to.
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='payment_items')
    
    # Link to the Medicine object from Medicine_Inventory app.
    # We use PROTECT to prevent a medicine from being deleted if it has been part of an invoice.
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, related_name='payment_items')
    
    # The quantity of this medicine sold.
    quantity = models.PositiveIntegerField(default=0)
    
    # The price per unit at the time of the transaction.
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # The total price for this item (quantity * price).
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name_plural = "Payment Items"

    def __str__(self):
        return f"{self.medicine.name} x {self.quantity} for Invoice #{self.payment.id}"
        
    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.price
        super().save(*args, **kwargs)
