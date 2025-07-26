from django.views import View
from django.utils import timezone
from django.shortcuts import render
from app.models import Flight, Reservation
from datetime import timedelta

class OffersView(View):
    def get(self, request):
        today = timezone.now().date()
        three_months = today + timedelta(days=90)
        offers = Flight.objects.filter(
            departure_time__date__gte=today,
            departure_time__date__lte=three_months,
            status='scheduled',
        ).order_by('departure_time')
        user_reservations = []
        if request.user.is_authenticated:
            user_reservations = list(Reservation.objects.filter(
                passenger__email=request.user.email,
                flight__in=offers
            ).values_list('flight_id', flat=True))
        return render(request, 'offers.html', {'offers': offers, 'user_reservations': user_reservations})
