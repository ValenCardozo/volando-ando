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

        # Check if passenger already has a reservation for this flight
        passenger = Passenger.objects.filter(email=request.user.email).first()
        if passenger and Reservation.objects.filter(flight=flight, passenger=passenger).exists():
            messages.error(request, "Ya tienes una reserva para este vuelo.")
            return redirect('offers')

        # Redirect to seat selection
        return redirect('seat_selection', flight_id=flight_id)
