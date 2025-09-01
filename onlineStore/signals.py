
from django.db.models.signals import post_save
from django.dispatch import receiver
from Medicine_inventory.models import Medicine
from Non_Medicine_inventory.models import NonMedicalProduct
from .models import Product # Use your actual Product model name

@receiver(post_save, sender=Medicine)
def create_or_update_product_from_medicine(sender, instance, created, **kwargs):
    """
    Listen for when a Medicine object is saved.
    If it's a new medicine, create a corresponding Product.
    If an existing medicine is updated, we don't need to do anything
    because the Product model just points to it.
    """
    if created:  # 'created' is True only the first time the object is saved
        Product.objects.create(
            product_type='Medicine',
            medicine=instance,
            # Set default availability. You can change this to False if you
            # want a manager to manually approve products for the store.
            available_online=True 
        )
        print(f"SIGNAL: Automatically created a Product for new medicine '{instance.name}'.")

@receiver(post_save, sender=NonMedicalProduct)
def create_or_update_product_from_non_medical(sender, instance, created, **kwargs):
    """
    Listen for when a NonMedicalProduct object is saved.
    If it's new, create a corresponding Product.
    """
    if created:
        Product.objects.create(
            product_type='NonMedicalProduct',
            non_medical_product=instance,
            available_online=True
        )
        print(f"SIGNAL: Automatically created a Product for new non-medical item '{instance.name}'.")