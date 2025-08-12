from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views import View
from home.forms import LoginForm, RegisterForm, FlightSearchForm
from app.models import Flight, Reservation, Passenger
from .offers_view import OffersView
from .buy_offer_view import BuyOfferView
from .my_flights_view import MyFlightsView
from .delete_reservation_view import DeleteReservationView
from .confirm_reservation_views import ConfirmReservationView, FinalizeReservationView

# Create your views here.
class HomeView(View):
    def get(self, request):
        form = FlightSearchForm(request.GET or None)
        flights = None
        user_reservations = []
        if request.user.is_authenticated and request.GET:
            if form.is_valid():
                origin = form.cleaned_data['origin']
                destination = form.cleaned_data['destination']
                departure_date = form.cleaned_data['departure_date']
                seat_class = form.cleaned_data['seat_class']
                flights = Flight.objects.filter(
                    origin=origin,
                    destination=destination,
                    departure_time__date=departure_date,
                    status='scheduled',
                )
                if seat_class:
                    flights = flights.filter(
                        airplane__seats__type=seat_class,
                        airplane__seats__status='available'
                    ).distinct()
                user_reservations = list(Reservation.objects.filter(
                    passenger__email=request.user.email,
                    flight__in=flights
                ).values_list('flight_id', flat=True))
        else:
            form = FlightSearchForm()
        return render(request, 'index.html', {'form': form, 'flights': flights, 'user_reservations': user_reservations})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(
            request,
            'accounts/register.html',
            {"form" : form }
        )

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email']
            )
            Passenger.objects.create(
                name=form.cleaned_data["username"],
                document=form.cleaned_data["document"],
                document_type=form.cleaned_data["document_type"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data["phone"],
                birth_date=form.cleaned_data["birth_date"]
            )
            messages.success(
                request,
                "Usuario registrado correctamente"
            )
            return redirect('login')
        return render(
            request,
            'accounts/register.html',
            {"form" : form }
        )


class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(
            request,
            'accounts/login.html',
            {"form": form}
        )

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                messages.success(request, "Sesion iniciada")
                return redirect("index")
            else:
                messages.error(request, "El usuario o contraseña no coinciden")

        return render(
            request,
            "accounts/login.html",
            {'form': form}
        )