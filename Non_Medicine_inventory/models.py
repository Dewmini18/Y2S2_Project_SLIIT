from django.db import models
from django.utils.text import slugify
from django.db.models import F

class NonMedicalProduct(models.Model):
    CATEGORY_CHOICES = [
        ('Cosmetics', 'Cosmetics'),
        ('Personal care', 'Personal Care'),
        ('Baby Products', 'Baby Products'),
        ('Supplements', 'Supplements'),
        ('Medical Devices', 'Medical Devices'),
        ('Other', 'Other'),
    ]

    brand = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True, null=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='non_medical_products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reorder_level = models.PositiveIntegerField(default=5)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Non-Medical Product'
        verbose_name_plural = 'Non-Medical Products'