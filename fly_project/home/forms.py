from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Nombre de Usuario",
        widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    password1 = forms.CharField(
        label="Contraseña",
        max_length=150,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )
    password2 = forms.CharField(
        label="Repita la contraseña",
        max_length=150,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        )
    )
    email = forms.EmailField(
        label="Correo Electronico",
        widget=forms.EmailInput(
            attrs={'class': 'form-control'}
        )
    )
    document_type = forms.ChoiceField(
        choices=[('DNI', 'DNI'), ('PASSPORT', 'Pasaporte')],
        label="Tipo de documento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    document = forms.CharField(
        max_length=30,
        label="Número de documento/pasaporte",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=30,
        label="Teléfono",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    birth_date = forms.DateField(
        label="Fecha de nacimiento",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Este nombre de usuario ya fue utilizado")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email de usuario ya fue utilizado")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pass1 = cleaned_data.get("password1")
        pass2 = cleaned_data.get("password2")

        if pass1 and pass2 and pass1 != pass2:
            raise ValidationError("Las contraseñas no coinciden")

    def clean_document(self):
        document = self.cleaned_data.get("document")
        doc_type = self.cleaned_data.get("document_type")
        if doc_type == "DNI":
            if not document.isdigit():
                raise ValidationError("El DNI debe contener solo números.")
            if not (7 <= len(document) <= 9):
                raise ValidationError("El DNI debe tener entre 7 y 9 dígitos.")
        elif doc_type == "PASSPORT":
            if len(document) < 5 or len(document) > 15:
                raise ValidationError("El pasaporte debe tener entre 5 y 15 caracteres.")
        return document

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        import re
        pattern = r'^[+]?[-\d\s]{7,15}$'
        if not re.match(pattern, phone):
            raise ValidationError("El teléfono debe ser válido y tener entre 7 y 15 caracteres. Solo se permiten números, espacios, guiones y el símbolo '+'.")
        return phone


class LoginForm(forms.Form):
    username=forms.CharField(
        label="Nombre de usuario",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                'class' : 'form-control'
            }
        )
    )
    password=forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control'
            }
        )
    )

CITY_CHOICES = [
    ("AEP", "Buenos Aires (Aeroparque)"),
    ("EZE", "Buenos Aires (Ezeiza)"),
    ("COR", "Córdoba"),
    ("MDZ", "Mendoza"),
    ("BRC", "Bariloche"),
    ("USH", "Ushuaia"),
    ("IGR", "Puerto Iguazú"),
    ("NQN", "Neuquén"),
]

CITY_SYNONYMS = {
    "aeroparque": "AEP",
    "buenos aires (aeroparque)": "AEP",
    "buenos aires": "AEP",
    "ezeiza": "EZE",
    "cordoba": "COR",
    "córdoba": "COR",
    "mendoza": "MDZ",
    "bariloche": "BRC",
    "san carlos de bariloche": "BRC",
    "ushuaia": "USH",
    "iguazu": "IGR",
    "iguazú": "IGR",
    "puerto iguazu": "IGR",
    "puerto iguazú": "IGR",
    "neuquen": "NQN",
    "neuquén": "NQN",
}

class FlightSearchForm(forms.Form):
    origin = forms.ChoiceField(choices=CITY_CHOICES, label="Origen", widget=forms.Select(attrs={'class': 'form-control'}))
    destination = forms.ChoiceField(choices=CITY_CHOICES, label="Destino", widget=forms.Select(attrs={'class': 'form-control'}))
    departure_date = forms.DateField(label="Fecha de ida", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    return_date = forms.DateField(label="Fecha de vuelta", required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    trip_type = forms.ChoiceField(choices=[('roundtrip', 'Ida y vuelta'), ('oneway', 'Solo ida')], widget=forms.RadioSelect)
    passengers = forms.IntegerField(min_value=1, max_value=6, label="Pasajeros", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    seat_class = forms.ChoiceField(choices=[('economy', 'Económica'), ('premium', 'Premium'), ('business', 'Business')], label="Clase", widget=forms.Select(attrs={'class': 'form-control'}))
