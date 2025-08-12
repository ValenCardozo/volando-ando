from django import forms
from app.models import Passenger
from django.core.exceptions import ValidationError

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Passenger
        fields = ['name', 'document', 'document_type', 'email', 'phone', 'birth_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.TextInput(attrs={'class': 'form-control'}),
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def clean_document(self):
        document = self.cleaned_data.get('document')
        doc_type = self.cleaned_data.get('document_type')
        qs = Passenger.objects.filter(document=document).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe un pasajero con ese documento.')
        if doc_type == 'DNI':
            if not document.isdigit():
                raise ValidationError('El DNI debe contener solo números.')
            if not (7 <= len(document) <= 9):
                raise ValidationError('El DNI debe tener entre 7 y 9 dígitos.')
        elif doc_type == 'PASSPORT':
            if len(document) < 5 or len(document) > 15:
                raise ValidationError('El pasaporte debe tener entre 5 y 15 caracteres.')
        return document

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = Passenger.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe un pasajero con ese email.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        import re
        pattern = r'^[+]?[-\d\s]{7,15}$'
        if not re.match(pattern, phone):
            raise ValidationError('El teléfono debe ser válido y tener entre 7 y 15 caracteres. Solo se permiten números, espacios, guiones y el símbolo "+".')
        return phone
