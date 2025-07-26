from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.utils import timezone
from app.models import Reservation

class MyFlightsView(LoginRequiredMixin, View):
    def get(self, request):
        reservations = Reservation.objects.filter(passenger__email=request.user.email).select_related('flight', 'seat')
        now = timezone.now()
        return render(request, 'my_flights.html', {'reservations': reservations, 'now': now})
