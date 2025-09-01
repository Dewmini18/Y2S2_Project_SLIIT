from django.conf import settings
from django.db import models
from Medicine_inventory.models import Medicine
from Non_Medicine_inventory.models import NonMedicalProduct

# Unified Products model to represent both Medicine and Non-Medical Products
class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('Medicine', 'Medicine'),
        ('NonMedicalProduct', 'NonMedicalProduct'),
    ]

    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    medicine = models.ForeignKey(
        Medicine, on_delete=models.CASCADE, null=True, blank=True
    )
    non_medical_product = models.ForeignKey(
        NonMedicalProduct, on_delete=models.CASCADE, null=True, blank=True
    )

    featured = models.BooleanField(default=False)
    available_online = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.product_type == 'Medicine' and self.medicine:
            return f"{self.medicine.name} ({self.medicine.dosage})"
        elif self.product_type == 'NonMedicalProduct' and self.non_medical_product:
            return f"{self.non_medical_product.name}"
        return "Unknown Product"

    # Unified display fields for templates and views
    @property
    def name(self):
        if self.product_type == 'Medicine' and self.medicine:
            return self.medicine.name
        elif self.product_type == 'NonMedicalProduct' and self.non_medical_product:
            return self.non_medical_product.name
        return "Unknown Product"

    @property
    def price(self):
        if self.product_type == 'Medicine' and self.medicine:
            return self.medicine.selling_price
        elif self.product_type == 'NonMedicalProduct' and self.non_medical_product:
            return self.non_medical_product.selling_price
        return 0

    @property
    def stock(self):
        if self.product_type == 'Medicine' and self.medicine:
            return self.medicine.quantity_in_stock
        elif self.product_type == 'NonMedicalProduct' and self.non_medical_product:
            return self.non_medical_product.quantity_in_stock
        return 0

    @property
    def image_url(self):
        if self.product_type == 'Medicine' and self.medicine:
            return self.medicine.image.url if self.medicine.image else ""
        elif self.product_type == 'NonMedicalProduct' and self.non_medical_product:
            return self.non_medical_product.image.url if self.non_medical_product.image else ""
        return ""

    @property
    def description(self):
        if self.product_type == 'Medicine' and self.medicine:
            return getattr(self.medicine, 'description', 'No description available')
        elif self.product_type == 'NonMedicalProduct' and self.non_medical_product:
            return getattr(self.non_medical_product, 'description', 'No description available')
        return ""

# Cart model to hold multiple items
class Cart(models.Model):
    cart_id = models.AutoField(primary_key=True)
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart({self.customer_user.username}, {self.created_at})"

# CartItem links products to cart with quantity
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"CartItem({self.product.name}, Qty: {self.quantity})"

# Order model for checkout
class Order(models.Model):
    ORDER_STATUS = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]

    order_id = models.AutoField(primary_key=True)
    customer_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='Pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order({self.customer_user.username}, {self.created_at})"

# Individual order items
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot of price at order time

    def __str__(self):
        return f"OrderItem({self.product.name}, Qty: {self.quantity})"
