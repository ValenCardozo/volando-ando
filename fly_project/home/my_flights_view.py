from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from app.models import Reservation, Flight, Passenger
from django.db.models import Count, Sum, Min, Max, Avg, Q

class MyFlightsView(LoginRequiredMixin, View):
    def get(self, request):
        # Obtener el pasajero asociado con el usuario actual
        passenger = get_object_or_404(Passenger, email=request.user.email)
        
        # Obtener todas las reservas del pasajero
        reservations = Reservation.objects.filter(passenger=passenger).select_related('flight', 'seat', 'ticket')
        now = timezone.now()
        
        # Calcular estadísticas
        stats = {
            'total_flights': reservations.count(),
            'upcoming_flights': reservations.filter(flight__departure_time__gt=now).count(),
            'past_flights': reservations.filter(flight__departure_time__lte=now).count(),
            'total_spent': reservations.aggregate(Sum('price'))['price__sum'] or 0,
            'most_visited': reservations.values('flight__destination').annotate(count=Count('id')).order_by('-count').first(),
        }
        
        # Obtener historial detallado
        past_flights = reservations.filter(flight__departure_time__lte=now).order_by('-flight__departure_time')
        upcoming_flights = reservations.filter(flight__departure_time__gt=now).order_by('flight__departure_time')
        
        # Ruta más frecuente
        frequent_routes = reservations.values('flight__origin', 'flight__destination').annotate(
            count=Count('id')
        ).order_by('-count')
        most_frequent_route = frequent_routes.first() if frequent_routes.exists() else None
        
        # Verificar si tiene boletos electrónicos
        for reservation in reservations:
            try:
                reservation.has_ticket = hasattr(reservation, 'ticket')
            except:
                reservation.has_ticket = False
        
        context = {
            'reservations': reservations,
            'now': now,
            'stats': stats,
            'past_flights': past_flights,
            'upcoming_flights': upcoming_flights,
            'most_frequent_route': most_frequent_route,
            'passenger': passenger,
        }
        
        return render(request, 'my_flights.html', context)
