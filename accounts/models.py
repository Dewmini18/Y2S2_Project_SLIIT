# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('pharmacist', 'Pharmacist'),
        ('cashier', 'Cashier'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')

    def __str__(self):
        return f"{self.username} ({self.role})"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Basic contact information
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Additional location information
    city = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    
    # National Identity Card
    nic = models.CharField(max_length=20, blank=True, null=True, verbose_name="NIC Number")
    
    def __str__(self):
        return self.user.username
    
    # Property methods to access User fields directly from Customer
    @property
    def id(self):
        return self.user.id
    
    @property
    def first_name(self):
        return self.user.first_name
    
    @property
    def last_name(self):
        return self.user.last_name
    
    @property
    def email(self):
        return self.user.email
    
    @property
    def date_joined(self):
        return self.user.date_joined
