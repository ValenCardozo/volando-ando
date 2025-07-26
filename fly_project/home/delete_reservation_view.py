from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from app.models import Reservation, Seat

class DeleteReservationView(LoginRequiredMixin, View):
    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id, passenger__email=request.user.email)
        # Liberar el asiento
        seat = reservation.seat
        seat.status = 'available'
        seat.save()
        reservation.delete()
        messages.success(request, "Reserva eliminada correctamente.")
        return redirect('my_flights')
