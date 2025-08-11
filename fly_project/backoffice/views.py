from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from app.models import Airplane, Flight, Seat, Reservation, Ticket, Passenger
from .forms import AirplaneForm, FlightForm, SeatForm

def is_superuser(user):
    return user.is_superuser

# Decorador para verificar que el usuario es superusuario
superuser_required = user_passes_test(is_superuser, login_url='login')

# Vista principal del backoffice
@superuser_required
def dashboard(request):
    flights_count = Flight.objects.count()
    airplanes_count = Airplane.objects.count()
    reservations_count = Reservation.objects.count()
    context = {
        'flights_count': flights_count,
        'airplanes_count': airplanes_count,
        'reservations_count': reservations_count,
    }
    return render(request, 'backoffice/dashboard.html', context)

# Vistas para Aviones (Airplane)
@method_decorator(superuser_required, name='dispatch')
class AirplaneListView(ListView):
    model = Airplane
    template_name = 'backoffice/airplane_list.html'
    context_object_name = 'airplanes'

@method_decorator(superuser_required, name='dispatch')
class AirplaneCreateView(CreateView):
    model = Airplane
    form_class = AirplaneForm
    template_name = 'backoffice/airplane_form.html'
    success_url = reverse_lazy('backoffice:airplane_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Avión creado exitosamente.")
        return super().form_valid(form)

@method_decorator(superuser_required, name='dispatch')
class AirplaneUpdateView(UpdateView):
    model = Airplane
    form_class = AirplaneForm
    template_name = 'backoffice/airplane_form.html'
    success_url = reverse_lazy('backoffice:airplane_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Avión actualizado exitosamente.")
        return super().form_valid(form)

@method_decorator(superuser_required, name='dispatch')
class AirplaneDeleteView(DeleteView):
    model = Airplane
    template_name = 'backoffice/airplane_confirm_delete.html'
    success_url = reverse_lazy('backoffice:airplane_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Avión eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)

@method_decorator(superuser_required, name='dispatch')
class AirplaneDetailView(DetailView):
    model = Airplane
    template_name = 'backoffice/airplane_detail.html'
    context_object_name = 'airplane'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seats'] = Seat.objects.filter(airplane=self.object)
        return context

# Vistas para Vuelos (Flight)
@method_decorator(superuser_required, name='dispatch')
class FlightListView(ListView):
    model = Flight
    template_name = 'backoffice/flight_list.html'
    context_object_name = 'flights'

@method_decorator(superuser_required, name='dispatch')
class FlightCreateView(CreateView):
    model = Flight
    form_class = FlightForm
    template_name = 'backoffice/flight_form.html'
    success_url = reverse_lazy('backoffice:flight_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Vuelo creado exitosamente.")
        return super().form_valid(form)

@method_decorator(superuser_required, name='dispatch')
class FlightUpdateView(UpdateView):
    model = Flight
    form_class = FlightForm
    template_name = 'backoffice/flight_form.html'
    success_url = reverse_lazy('backoffice:flight_list')
    
    def form_valid(self, form):
        messages.success(self.request, "Vuelo actualizado exitosamente.")
        return super().form_valid(form)

@method_decorator(superuser_required, name='dispatch')
class FlightDeleteView(DeleteView):
    model = Flight
    template_name = 'backoffice/flight_confirm_delete.html'
    success_url = reverse_lazy('backoffice:flight_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, "Vuelo eliminado exitosamente.")
        return super().delete(request, *args, **kwargs)

@method_decorator(superuser_required, name='dispatch')
class FlightDetailView(DetailView):
    model = Flight
    template_name = 'backoffice/flight_detail.html'
    context_object_name = 'flight'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservations'] = Reservation.objects.filter(flight=self.object)
        return context

# Vistas para Asientos (Seat)
@superuser_required
def seat_management(request, airplane_id):
    airplane = get_object_or_404(Airplane, id=airplane_id)
    seats = Seat.objects.filter(airplane=airplane)
    
    if request.method == 'POST':
        form = SeatForm(request.POST)
        if form.is_valid():
            seat = form.save(commit=False)
            seat.airplane = airplane
            seat.save()
            messages.success(request, "Asiento creado exitosamente.")
            return redirect('backoffice:seat_management', airplane_id=airplane_id)
    else:
        form = SeatForm()
    
    return render(request, 'backoffice/seat_management.html', {
        'airplane': airplane,
        'seats': seats,
        'form': form
    })

@superuser_required
def seat_update(request, pk):
    seat = get_object_or_404(Seat, id=pk)
    
    if request.method == 'POST':
        form = SeatForm(request.POST, instance=seat)
        if form.is_valid():
            form.save()
            messages.success(request, "Asiento actualizado exitosamente.")
            return redirect('backoffice:seat_management', airplane_id=seat.airplane.id)
    else:
        form = SeatForm(instance=seat)
    
    return render(request, 'backoffice/seat_form.html', {'form': form, 'seat': seat})

@superuser_required
def seat_delete(request, pk):
    seat = get_object_or_404(Seat, id=pk)
    airplane_id = seat.airplane.id
    
    if request.method == 'POST':
        seat.delete()
        messages.success(request, "Asiento eliminado exitosamente.")
        return redirect('backoffice:seat_management', airplane_id=airplane_id)
    
    return render(request, 'backoffice/seat_confirm_delete.html', {'seat': seat})

# Vista para generar layout de asientos
@superuser_required
def generate_seats(request, airplane_id):
    airplane = get_object_or_404(Airplane, id=airplane_id)
    
    if request.method == 'POST':
        # Eliminar asientos existentes
        Seat.objects.filter(airplane=airplane).delete()
        
        # Obtener parámetros del formulario
        rows = airplane.rows
        cols = airplane.columns
        seat_type = request.POST.get('seat_type', 'economy')
        
        # Generar asientos
        for row in range(1, rows + 1):
            for col in range(1, cols + 1):
                seat_number = f"{row}{chr(64 + col)}"  # 1A, 1B, etc.
                Seat.objects.create(
                    airplane=airplane,
                    number=seat_number,
                    row=row,
                    column=col,
                    type=seat_type,
                    status='available'
                )
        
        messages.success(request, f"Se generaron {rows * cols} asientos exitosamente.")
        return redirect('backoffice:seat_management', airplane_id=airplane_id)
    
    return render(request, 'backoffice/generate_seats.html', {'airplane': airplane})

# Vistas para informes y estadísticas
@superuser_required
def flight_statistics(request):
    flights = Flight.objects.all()
    
    # Estadísticas básicas
    total_flights = flights.count()
    scheduled_flights = flights.filter(status='scheduled').count()
    completed_flights = flights.filter(status='completed').count()
    canceled_flights = flights.filter(status='canceled').count()
    
    context = {
        'total_flights': total_flights,
        'scheduled_flights': scheduled_flights,
        'completed_flights': completed_flights,
        'canceled_flights': canceled_flights,
    }
    
    return render(request, 'backoffice/flight_statistics.html', context)

@superuser_required
def reservation_statistics(request):
    reservations = Reservation.objects.all()
    
    # Estadísticas básicas
    total_reservations = reservations.count()
    confirmed_reservations = reservations.filter(status='confirmed').count()
    pending_reservations = reservations.filter(status='pending').count()
    canceled_reservations = reservations.filter(status='canceled').count()
    
    context = {
        'total_reservations': total_reservations,
        'confirmed_reservations': confirmed_reservations,
        'pending_reservations': pending_reservations,
        'canceled_reservations': canceled_reservations,
    }
    
    return render(request, 'backoffice/reservation_statistics.html', context)