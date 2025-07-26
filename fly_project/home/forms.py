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
