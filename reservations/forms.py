from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Apartment, Reservation, Tenant

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class TenantProfileForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['phone', 'address', 'emergency_contact', 'emergency_phone', 'id_number']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+63 XXX XXX XXXX'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-input'}),
            'emergency_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+63 XXX XXX XXXX'}),
            'id_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Government ID Number'}),
        }

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['name', 'apartment_type', 'floor', 'unit_number', 'price_per_month', 
                  'size_sqm', 'bedrooms', 'bathrooms', 'status', 'description', 'amenities', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Compound Name'}),
            'unit_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Room/Unit #'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'price_per_month': forms.NumberInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['apartment', 'check_in', 'special_requests']
        widgets = {
            'apartment': forms.Select(attrs={'class': 'form-select searchable-select'}),
            'check_in': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'special_requests': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Any specific requests?'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show ALL available apartments
        self.fields['apartment'].queryset = Apartment.objects.filter(status='available')
        # Custom label for the dropdown
        self.fields['apartment'].label_from_instance = lambda obj: f"Unit {obj.unit_number} - {obj.name} (₱{obj.price_per_month}/mo)"
    
    def clean_apartment(self):
        apartment = self.cleaned_data.get('apartment')
        
        # Check if apartment is still available
        if apartment and apartment.status != 'available':
            raise forms.ValidationError(
                f"Unit {apartment.unit_number} is no longer available. "
                f"Current status: {apartment.get_status_display()}"
            )
        
        return apartment