from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from app.models import Flight, Seat, Passenger, Reservation, Ticket
from django.http import HttpResponse
import os
from django.conf import settings
import mimetypes
from decimal import Decimal

@method_decorator(login_required, name='dispatch')
class SeatSelectionView(View):
    def get(self, request, flight_id):
        flight = get_object_or_404(Flight, id=flight_id, status='scheduled')
        
        # Get all seats for the flight's airplane
        seats = Seat.objects.filter(airplane=flight.airplane)
        
        # Check if user already has a reservation for this flight
        passenger = Passenger.objects.filter(email=request.user.email).first()
        has_reservation = False
        user_seat = None
        
        if passenger:
            reservation = Reservation.objects.filter(flight=flight, passenger=passenger).first()
            if reservation:
                has_reservation = True
                user_seat = reservation.seat
        
        # Organize seats by rows and columns for better display
        seat_map = {}
        for row in range(1, flight.airplane.rows + 1):
            seat_map[row] = {}
            for col in range(1, flight.airplane.columns + 1):
                col_letter = chr(64 + col)  # Convert column number to letter (1=A, 2=B, etc.)
                seat_map[row][col_letter] = None
        
        # Fill the seat map with actual seat data
        for seat in seats:
            col_letter = chr(64 + seat.column)
            seat_map[seat.row][col_letter] = seat
        
        # Get prices for different seat types
        prices = {
            'economy': flight.base_price,
            'premium': flight.base_price * Decimal('1.5'),
            'business': flight.base_price * Decimal('2.0')
        }
        
        return render(request, 'seat_selection.html', {
            'flight': flight,
            'seat_map': seat_map,
            'has_reservation': has_reservation,
            'user_seat': user_seat,
            'prices': prices,
            'rows': range(1, flight.airplane.rows + 1),
            'columns': [chr(64 + col) for col in range(1, flight.airplane.columns + 1)]
        })
    
    def post(self, request, flight_id):
        flight = get_object_or_404(Flight, id=flight_id, status='scheduled')
        seat_id = request.POST.get('seat_id')
        
        if not seat_id:
            messages.error(request, "Debes seleccionar un asiento.")
            return redirect('seat_selection', flight_id=flight_id)
        
        seat = get_object_or_404(Seat, id=seat_id)
        
        # Check if seat is available
        if seat.status != 'available':
            messages.error(request, "El asiento seleccionado ya no está disponible.")
            return redirect('seat_selection', flight_id=flight_id)
        
        # Check if user already has a reservation
        passenger = Passenger.objects.filter(email=request.user.email).first()
        if passenger:
            existing_reservation = Reservation.objects.filter(flight=flight, passenger=passenger).first()
            if existing_reservation:
                # Release the previously reserved seat
                old_seat = existing_reservation.seat
                old_seat.status = 'available'
                old_seat.save()
                
                # Update with the new seat
                existing_reservation.seat = seat
                existing_reservation.save()
                
                # Mark the new seat as reserved
                seat.status = 'reserved'
                seat.save()
                
                messages.success(request, "Tu asiento ha sido actualizado correctamente.")
                return redirect('confirm_reservation', flight_id=flight_id, seat_id=seat.id)
        
        # If no existing reservation, mark the seat as reserved
        seat.status = 'reserved'
        seat.save()
        
        # Redirect to the confirmation page
        return redirect('confirm_reservation', flight_id=flight_id, seat_id=seat.id)

def download_ticket(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    
    if hasattr(reservation, 'ticket'):
        ticket_path = os.path.join(settings.MEDIA_ROOT, f'tickets/ticket_{reservation.reservation_code}.pdf')
        
        if os.path.exists(ticket_path):
            with open(ticket_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type="application/pdf")
                response['Content-Disposition'] = f'inline; filename=ticket_{reservation.reservation_code}.pdf'
                return response
    
    messages.error(request, "El ticket no está disponible.")
    return redirect('my_flights')