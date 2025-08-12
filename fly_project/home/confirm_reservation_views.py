from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from app.models import Flight, Seat, Passenger, Reservation, Ticket
from django.views import View
from django.conf import settings
import random
import string
from decimal import Decimal
from .utils.ticket_generator import generate_ticket_pdf

@method_decorator(login_required, name='dispatch')
class ConfirmReservationView(View):
    def post(self, request, flight_id):
        flight = get_object_or_404(Flight, id=flight_id, status='scheduled')
        
        # Redirigir a la selección de asientos si no se ha seleccionado ninguno
        return redirect('seat_selection', flight_id=flight_id)
        
    def get(self, request, flight_id, seat_id=None):
        if not seat_id:
            # Si no se proporciona seat_id, redirigir a la selección de asientos
            return redirect('seat_selection', flight_id=flight_id)
            
        flight = get_object_or_404(Flight, id=flight_id, status='scheduled')
        seat = get_object_or_404(Seat, id=seat_id, status='reserved')
        
        # Verificar que el asiento pertenezca al avión del vuelo
        if seat.airplane != flight.airplane:
            messages.error(request, "El asiento seleccionado no pertenece a este vuelo.")
            return redirect('seat_selection', flight_id=flight_id)
            
        passenger = Passenger.objects.filter(email=request.user.email).first()
        if passenger and Reservation.objects.filter(flight=flight, passenger=passenger).exists():
            reservation = Reservation.objects.get(flight=flight, passenger=passenger)
            if reservation.seat.id != seat.id:
                messages.error(request, "Ya tienes una reserva para este vuelo con un asiento diferente.")
                return redirect('my_flights')
            
        # Definir el precio basado en el tipo de asiento
        price = flight.base_price
        if seat.type == 'premium':
            price = flight.base_price * Decimal('1.5')
        elif seat.type == 'business':
            price = flight.base_price * Decimal('2.0')
            
        return render(request, 'confirm_reservation_prompt.html', {
            'flight': flight, 
            'seat': seat,
            'price': price
        })

@method_decorator(login_required, name='dispatch')
class FinalizeReservationView(View):
    def post(self, request, flight_id):
        flight = get_object_or_404(Flight, id=flight_id, status='scheduled')
        
        # Obtener el asiento seleccionado del parámetro oculto
        seat_id = request.POST.get('seat_id')
        if not seat_id:
            messages.error(request, "No se ha seleccionado un asiento.")
            return redirect('seat_selection', flight_id=flight_id)
            
        seat = get_object_or_404(Seat, id=seat_id)
        
        # Verificar que el asiento esté disponible o reservado
        if seat.status not in ['available', 'reserved']:
            messages.error(request, "El asiento seleccionado ya no está disponible.")
            return redirect('seat_selection', flight_id=flight_id)
            
        passenger, _ = Passenger.objects.get_or_create(
            email=request.user.email,
            defaults={
                'name': request.user.username,
                'document': f'user-{request.user.id}',
                'document_type': 'OTHER',
                'phone': '',
                'birth_date': '2000-01-01',
            }
        )
        
        # Verificar si ya existe una reserva
        existing_reservation = Reservation.objects.filter(flight=flight, passenger=passenger).first()
        if existing_reservation:
            # Si la reserva es para un asiento diferente, actualizarla
            if existing_reservation.seat.id != seat.id:
                # Liberar el antiguo asiento
                old_seat = existing_reservation.seat
                old_seat.status = 'available'
                old_seat.save()
                
                # Actualizar la reserva con el nuevo asiento
                existing_reservation.seat = seat
                existing_reservation.save()
                
                # Actualizar el boleto si existe
                if hasattr(existing_reservation, 'ticket'):
                    ticket = existing_reservation.ticket
                else:
                    # Generar código de barras para el boleto
                    barcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                    while Ticket.objects.filter(barcode=barcode).exists():
                        barcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                    
                    # Crear boleto
                    ticket = Ticket.objects.create(
                        reservation=existing_reservation,
                        barcode=barcode,
                        status="issued"
                    )
                
                # Generar PDF del boleto
                generate_ticket_pdf(existing_reservation)
                
                # Marcar el asiento como ocupado
                seat.status = 'occupied'
                seat.save()
                
                messages.success(request, "Tu reserva ha sido actualizada exitosamente.")
                return render(request, 'confirm_reservation.html', {
                    'reservation': existing_reservation,
                    'ticket': ticket
                })
            else:
                messages.info(request, "Ya tienes una reserva para este vuelo con este mismo asiento.")
                return redirect('my_flights')
            
        # Generar código de reserva único
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while Reservation.objects.filter(reservation_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # Definir el precio basado en el tipo de asiento
        price = flight.base_price
        if seat.type == 'premium':
            price = flight.base_price * Decimal('1.5')
        elif seat.type == 'business':
            price = flight.base_price * Decimal('2.0')
            
        # Crear la reserva
        reservation = Reservation.objects.create(
            flight=flight,
            passenger=passenger,
            seat=seat,
            status='confirmed',
            price=price,
            reservation_code=code
        )
        
        # Actualizar el estado del asiento
        seat.status = 'occupied'
        seat.save()
        
        # Generar código de barras para el boleto
        barcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        while Ticket.objects.filter(barcode=barcode).exists():
            barcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        
        # Crear boleto
        ticket = Ticket.objects.create(
            reservation=reservation,
            barcode=barcode,
            status="issued"
        )
        
        # Generar PDF del boleto
        generate_ticket_pdf(reservation)
        
        return render(request, 'confirm_reservation.html', {
            'reservation': reservation,
            'ticket': ticket
        })
