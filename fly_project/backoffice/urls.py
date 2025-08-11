from django.urls import path
from . import views

app_name = 'backoffice'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Airplane URLs
    path('airplanes/', views.AirplaneListView.as_view(), name='airplane_list'),
    path('airplanes/add/', views.AirplaneCreateView.as_view(), name='airplane_create'),
    path('airplanes/<int:pk>/', views.AirplaneDetailView.as_view(), name='airplane_detail'),
    path('airplanes/<int:pk>/edit/', views.AirplaneUpdateView.as_view(), name='airplane_update'),
    path('airplanes/<int:pk>/delete/', views.AirplaneDeleteView.as_view(), name='airplane_delete'),
    
    # Flight URLs
    path('flights/', views.FlightListView.as_view(), name='flight_list'),
    path('flights/add/', views.FlightCreateView.as_view(), name='flight_create'),
    path('flights/<int:pk>/', views.FlightDetailView.as_view(), name='flight_detail'),
    path('flights/<int:pk>/edit/', views.FlightUpdateView.as_view(), name='flight_update'),
    path('flights/<int:pk>/delete/', views.FlightDeleteView.as_view(), name='flight_delete'),
    
    # Seat URLs
    path('airplanes/<int:airplane_id>/seats/', views.seat_management, name='seat_management'),
    path('seats/<int:pk>/edit/', views.seat_update, name='seat_update'),
    path('seats/<int:pk>/delete/', views.seat_delete, name='seat_delete'),
    path('airplanes/<int:airplane_id>/generate-seats/', views.generate_seats, name='generate_seats'),
    
    # Statistics URLs
    path('statistics/flights/', views.flight_statistics, name='flight_statistics'),
    path('statistics/reservations/', views.reservation_statistics, name='reservation_statistics'),
]