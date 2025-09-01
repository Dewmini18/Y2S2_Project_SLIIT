
from django.core.management.base import BaseCommand
from django.db.models import F

from onlineStore.models import Product
from Medicine_inventory.models import Medicine
from Non_Medicine_inventory.models import NonMedicalProduct

class Command(BaseCommand):
    help = 'Syncs existing inventory items to the online store Product table.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting product synchronization...'))

        # --- Sync Medicines ---
        self.stdout.write('Checking for existing Medicines to sync...')
        
        # Find all Medicine IDs that are already linked in the Product table
        existing_medicine_ids = Product.objects.filter(
            medicine__isnull=False
        ).values_list('medicine_id', flat=True)

        # Find all Medicines that are NOT in that list
        medicines_to_sync = Medicine.objects.exclude(id__in=existing_medicine_ids)
        
        count = 0
        for med in medicines_to_sync:
            Product.objects.create(
                product_type='Medicine',
                medicine=med,
                available_online=True # Or False if you want to manually approve
            )
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} new Product(s) for existing Medicines.'))

        # --- Sync Non-Medical Products ---
        self.stdout.write('Checking for existing Non-Medical Products to sync...')

        # Find all NonMedicalProduct IDs that are already linked
        existing_non_medical_ids = Product.objects.filter(
            non_medical_product__isnull=False
        ).values_list('non_medical_product_id', flat=True)

        # Find all NonMedicalProducts that are NOT in that list
        non_medicals_to_sync = NonMedicalProduct.objects.exclude(id__in=existing_non_medical_ids)

        count = 0
        for item in non_medicals_to_sync:
            Product.objects.create(
                product_type='NonMedicalProduct',
                non_medical_product=item,
                available_online=True
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} new Product(s) for existing Non-Medical items.'))
        self.stdout.write(self.style.SUCCESS('Synchronization complete.'))