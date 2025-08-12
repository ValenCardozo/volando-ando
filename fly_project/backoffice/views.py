from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
from app.models import Airplane, Flight, Seat, Reservation, Ticket, Passenger, Destination, DestinationImage
from .forms import AirplaneForm, FlightForm, SeatForm
import csv
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime
import io

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

class PopularDestinationsView(TemplateView):
    template_name = "backoffice/popular_destinations.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['destinations'] = [
            {
                "name": dest.name,
                "image": img.image_url if img else "img/default.jpg"
            }
            for dest in Destination.objects.all()
            for img in [dest.images.first()]
        ]

        print(context['destinations'])  # Debugging line to check the context data
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

# Vista para listar pasajeros por vuelo
@superuser_required
def flight_passengers(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    reservations = Reservation.objects.filter(flight=flight).select_related('passenger', 'seat')
    
    # Verificar si se solicita exportar como CSV
    if 'export' in request.GET:
        # Crear un archivo CSV en memoria
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        
        # Escribir encabezados
        writer.writerow([
            'ID Reserva', 
            'Código Reserva', 
            'Nombre Pasajero', 
            'Documento', 
            'Tipo de Documento', 
            'Email', 
            'Teléfono', 
            'Asiento', 
            'Clase', 
            'Precio'
        ])
        
        # Escribir datos
        for r in reservations:
            writer.writerow([
                r.id,
                r.reservation_code,
                r.passenger.name,
                r.passenger.document,
                r.passenger.document_type,
                r.passenger.email,
                r.passenger.phone,
                r.seat.number,
                r.seat.get_type_display(),
                r.price
            ])
        
        # Crear respuesta HTTP con el CSV
        response = HttpResponse(buffer.getvalue(), content_type='text/csv')
        current_date = timezone.now().strftime('%Y%m%d')
        filename = f"pasajeros_vuelo_{flight.id}_{current_date}.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    # Estadísticas
    stats = {
        'total_passengers': reservations.count(),
        'economy_class': reservations.filter(seat__type='economy').count(),
        'premium_class': reservations.filter(seat__type='premium').count(),
        'business_class': reservations.filter(seat__type='business').count(),
        'capacity': flight.airplane.capacity,
        'occupancy_rate': (reservations.count() / flight.airplane.capacity * 100) if flight.airplane.capacity > 0 else 0,
    }
    
    context = {
        'flight': flight,
        'reservations': reservations,
        'stats': stats,
    }
    
    return render(request, 'backoffice/flight_passengers.html', context)


# Vista para generar un PDF con el listado de pasajeros
@superuser_required
def flight_passengers_pdf(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    reservations = Reservation.objects.filter(flight=flight).select_related('passenger', 'seat')
    
    # Importamos aquí para evitar dependencias circulares
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    # Crear un buffer de bytes para el PDF
    buffer = io.BytesIO()
    
    # Crear el documento PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Lista para almacenar los elementos del PDF
    elements = []
    
    # Título
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        alignment=1,
        spaceAfter=12,
    )
    elements.append(Paragraph(f"Listado de Pasajeros - Vuelo {flight.id}", title_style))
    elements.append(Spacer(1, 12))
    
    # Detalles del vuelo
    flight_info = f"""
    <b>Vuelo:</b> {flight.id}<br/>
    <b>Origen:</b> {flight.origin}<br/>
    <b>Destino:</b> {flight.destination}<br/>
    <b>Fecha de salida:</b> {flight.departure_time.strftime('%d/%m/%Y %H:%M')}<br/>
    <b>Estado:</b> {flight.get_status_display()}<br/>
    <b>Avión:</b> {flight.airplane.model} (Capacidad: {flight.airplane.capacity})
    """
    elements.append(Paragraph(flight_info, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Estadísticas
    total_passengers = reservations.count()
    occupancy_rate = (total_passengers / flight.airplane.capacity * 100) if flight.airplane.capacity > 0 else 0
    
    stats_info = f"""
    <b>Total de pasajeros:</b> {total_passengers} de {flight.airplane.capacity} ({occupancy_rate:.1f}%)<br/>
    <b>Clase Económica:</b> {reservations.filter(seat__type='economy').count()}<br/>
    <b>Clase Premium:</b> {reservations.filter(seat__type='premium').count()}<br/>
    <b>Clase Business:</b> {reservations.filter(seat__type='business').count()}
    """
    elements.append(Paragraph(stats_info, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Tabla de pasajeros
    data = [
        ['Asiento', 'Pasajero', 'Documento', 'Email', 'Teléfono', 'Clase']
    ]
    
    for r in reservations:
        data.append([
            r.seat.number,
            r.passenger.name,
            f"{r.passenger.document_type}: {r.passenger.document}",
            r.passenger.email,
            r.passenger.phone,
            r.seat.get_type_display()
        ])
    
    # Crear tabla
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(table)
    
    # Agregar pie de página
    elements.append(Spacer(1, 20))
    footer_text = f"Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Volando Ando"
    elements.append(Paragraph(footer_text, styles['Italic']))
    
    # Construir PDF
    doc.build(elements)
    
    # Obtener el valor del buffer y crear respuesta HTTP
    pdf_value = buffer.getvalue()
    buffer.close()
    
    # Crear respuesta con el PDF
    response = HttpResponse(content_type='application/pdf')
    current_date = timezone.now().strftime('%Y%m%d')
    filename = f"pasajeros_vuelo_{flight.id}_{current_date}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf_value)
    
    return response