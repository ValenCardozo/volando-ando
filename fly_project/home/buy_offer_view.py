from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from app.models import Flight, Seat, Passenger, Reservation
from django.utils import timezone
from django.views import View
import random
import string

@method_decorator(login_required, name='dispatch')
class BuyOfferView(View):
    def post(self, request, flight_id):
        flight = get_object_or_404(Flight, id=flight_id, status='scheduled')

        seat = flight.airplane.seats.filter(status='available').first()
        if not seat:
            messages.error(request, "No hay asientos disponibles para este vuelo.")
            return redirect('offers')

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

        if Reservation.objects.filter(flight=flight, passenger=passenger).exists():
            messages.error(request, "Ya tienes una reserva para este vuelo.")
            return redirect('offers')

        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        while Reservation.objects.filter(reservation_code=code).exists():
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

        reservation = Reservation.objects.create(
            flight=flight,
            passenger=passenger,
            seat=seat,
            status='confirmed',
            price=flight.base_price,
            reservation_code=code
        )

        seat.status = 'occupied'
        seat.save()
        return render(request, 'confirm_reservation.html', {'reservation': reservation})
