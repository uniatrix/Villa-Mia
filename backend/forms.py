from django import forms
from .models import Room, Booking, NewsletterEmail

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['title', 'description', 'image', 'capacity', 'tv', 'wifi', 'ac', 'bathtub', 'price', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'tv': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'wifi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ac': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bathtub': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }

class RoomCategoryForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['category', 'available']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['guest_name', 'phone_number', 'check_in', 'check_out', 'adults', 'children']
        widgets = {
            'guest_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 13}),
            'check_in': forms.HiddenInput(),
            'check_out': forms.HiddenInput(),
            'adults': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10}),
            'children': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 10}),
        }
        labels = {
            'guest_name': 'Nome Completo',
            'phone_number': 'Telefone',
            'adults': 'Adultos',
            'children': 'Crianças',
        }

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.fields['guest_name'].required = True
        self.fields['phone_number'].required = True
        self.fields['adults'].initial = 1
        self.fields['children'].initial = 0

    def clean_guest_name(self):
        guest_name = self.cleaned_data.get('guest_name')
        if len(guest_name) <= 4:
            self.add_error('guest_name', "O nome deve ter mais de 4 caracteres")
        return guest_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            self.add_error('phone_number', "O telefone deve conter apenas dígitos")
        if len(phone_number) < 11:
            self.add_error('phone_number', "O telefone deve ter pelo menos 11 dígitos")
        if len(phone_number) > 13:
            self.add_error('phone_number', "O telefone deve ter até 13 dígitos")
        return phone_number
    
class NewsletterEmailForm(forms.ModelForm):
    class Meta:
        model = NewsletterEmail
        fields = ['email']