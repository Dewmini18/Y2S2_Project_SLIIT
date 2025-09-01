from django import forms
from .models import NonMedicalProduct
from django.utils.text import slugify

class NonMedicalProductForm(forms.ModelForm):
    class Meta:
        model = NonMedicalProduct
        fields = ['brand', 'name', 'category', 'description', 'cost_price',
                  'selling_price', 'stock', 'image', 'is_active', 'reorder_level', 'slug']
        widgets = {
            'brand': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none py-1'}),
            'name': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none py-1'}),
            'category': forms.Select(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none py-1'}),
            'description': forms.Textarea(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none', 'rows': 3}),
            'cost_price': forms.NumberInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none py-1' , 'step': '0.01' }),
            'selling_price': forms.NumberInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none py-1', 'step': '0.01'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none py-1'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none py-1'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none py-1'}),
            'slug': forms.TextInput(attrs={'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-500 focus:ring-opacity-50 focus:outline-none py-1', 'placeholder': 'Leave blank to auto-generate'}),
        }
    
    def clean_slug(self):
        """Clean and validate the slug field"""
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        # If no slug is provided, generate it from the name
        if not slug and name:
            return slugify(name)
        
        # If a slug is provided, ensure it's properly slugified
        if slug:
            return slugify(slug)
        
        return slug