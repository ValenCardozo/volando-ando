from django import forms
from app.models import Airplane, Flight, Seat
from datetime import timedelta

class AirplaneForm(forms.ModelForm):
    class Meta:
        model = Airplane
        fields = ['model', 'capacity', 'rows', 'columns']
        widgets = {
            'model': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'rows': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'columns': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        labels = {
            'model': 'Modelo del avión',
            'capacity': 'Capacidad (pasajeros)',
            'rows': 'Filas',
            'columns': 'Columnas',
        }

class FlightForm(forms.ModelForm):
    duration_hours = forms.IntegerField(
        min_value=0, 
        label='Duración (horas)', 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    duration_minutes = forms.IntegerField(
        min_value=0, 
        max_value=59, 
        label='Duración (minutos)', 
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Flight
        fields = [
            'airplane', 'origin', 'destination', 
            'departure_time', 'arrival_time', 
            'status', 'base_price'
        ]
        widgets = {
            'airplane': forms.Select(attrs={'class': 'form-control'}),
            'origin': forms.TextInput(attrs={'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'arrival_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
        }
        labels = {
            'airplane': 'Avión',
            'origin': 'Origen',
            'destination': 'Destino',
            'departure_time': 'Fecha y hora de salida',
            'arrival_time': 'Fecha y hora de llegada',
            'status': 'Estado',
            'base_price': 'Precio base',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            duration = self.instance.duration
            self.fields['duration_hours'].initial = duration.seconds // 3600
            self.fields['duration_minutes'].initial = (duration.seconds % 3600) // 60

    def clean(self):
        cleaned_data = super().clean()
        departure_time = cleaned_data.get('departure_time')
        arrival_time = cleaned_data.get('arrival_time')
        
        if departure_time and arrival_time:
            if arrival_time <= departure_time:
                raise forms.ValidationError("La hora de llegada debe ser posterior a la hora de salida.")
        
        duration_hours = cleaned_data.get('duration_hours', 0)
        duration_minutes = cleaned_data.get('duration_minutes', 0)
        duration = timedelta(hours=duration_hours, minutes=duration_minutes)
        cleaned_data['duration'] = duration
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        duration_hours = self.cleaned_data.get('duration_hours', 0)
        duration_minutes = self.cleaned_data.get('duration_minutes', 0)
        instance.duration = timedelta(hours=duration_hours, minutes=duration_minutes)
        
        if commit:
            instance.save()
        return instance

class SeatForm(forms.ModelForm):
    class Meta:
        model = Seat
        fields = ['number', 'row', 'column', 'type', 'status']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'row': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'column': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'number': 'Número de asiento',
            'row': 'Fila',
            'column': 'Columna',
            'type': 'Tipo',
            'status': 'Estado',
        }