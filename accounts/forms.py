# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Customer  # Use your actual model name

User = get_user_model()  # This gets your custom User model

class CustomerSignUpForm(UserCreationForm):
    # User fields
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    # Customer profile fields
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={
    'rows': 3, 
    'class': 'mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 shadow-sm focus:border-cyan-500 focus:ring-cyan-500'
}), required=False)
    city = forms.CharField(max_length=100, required=False)
    postal_code = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=100, required=False)
    nic = forms.CharField(max_length=20, required=False, label="NIC Number")
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2", "first_name", "last_name")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = "customer"
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        
        if commit:
            user.save()
            # Create customer profile with ALL fields
            Customer.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', ''),
                address=self.cleaned_data.get('address', ''),
                city=self.cleaned_data.get('city', ''),
                postal_code=self.cleaned_data.get('postal_code', ''),
                country=self.cleaned_data.get('country', ''),
                nic=self.cleaned_data.get('nic', '')
            )
        return user


class StaffCreationForm(forms.ModelForm):
    # Make passwords optional for editing staff
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput, required=False)
    
    ROLE_CHOICES = (
        ('pharmacist', 'Pharmacist'),
        ('cashier', 'Cashier'),
    )
    role = forms.ChoiceField(choices=ROLE_CHOICES)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If instance exists (editing mode), make passwords optional
        if self.instance and self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            # Make sure initial values are set
            self.initial['email'] = self.instance.email
            self.initial['role'] = self.instance.role

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.instance and self.instance.pk:
            if User.objects.exclude(pk=self.instance.pk).filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        else:
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("This username is already taken.")
        return username
        
    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        
        # Always update these fields
        user.role = self.cleaned_data["role"]
        user.email = self.cleaned_data["email"]
        
        # Only set password if both password fields are provided
        if self.cleaned_data.get("password1"):
            user.set_password(self.cleaned_data["password1"])
            
        if commit:
            user.save()
        return user


class CustomerProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    
    class Meta:
        model = Customer
        fields = ['phone', 'address', 'city', 'postal_code', 'country', 'nic']
    
    # Make sure initialization includes all fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

    def clean_username(self):
        username = self.cleaned_data['username']
        # Using the custom User model via get_user_model()
        if User.objects.exclude(pk=self.instance.user.pk).filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        
        # Update user fields
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Update profile fields
        profile.phone = self.cleaned_data['phone']
        profile.address = self.cleaned_data['address']
        profile.city = self.cleaned_data['city']
        profile.postal_code = self.cleaned_data['postal_code']
        profile.country = self.cleaned_data['country']
        profile.nic = self.cleaned_data['nic']
        
        if commit:
            user.save()
            profile.save()
        return profile