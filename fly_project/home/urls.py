from django.urls import path

from home.views import (
    HomeView,
    LoginView,
    LogoutView,
    RegisterView,
    OffersView,
    BuyOfferView,
    MyFlightsView,
    DeleteReservationView,
    ConfirmReservationView,
    FinalizeReservationView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('offers/', OffersView.as_view(), name='offers'),
    path('buy-offer/<int:flight_id>/', BuyOfferView.as_view(), name='buy_offer'),
    path('my-flights/', MyFlightsView.as_view(), name='my_flights'),
    path('delete-reservation/<int:reservation_id>/', DeleteReservationView.as_view(), name='delete_reservation'),
    path('confirm-reservation/<int:flight_id>/', ConfirmReservationView.as_view(), name='confirm_reservation_prompt'),
    path('finalize-reservation/<int:flight_id>/', FinalizeReservationView.as_view(), name='finalize_reservation'),
    path('', HomeView.as_view(), name='index'),
]