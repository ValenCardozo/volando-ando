from django.contrib import admin
from app.models import Airplane, Flight, Passenger, Seat, Reservation, Ticket, Destination, DestinationImage

@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ('model', 'capacity', 'rows', 'columns')
    search_fields = ('model',)
    list_filter = ('capacity',)

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'origin', 'destination', 'departure_time', 'arrival_time', 'status', 'base_price')
    list_filter = ('status', 'origin', 'destination', 'departure_time')
    search_fields = ('origin', 'destination')

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('name', 'document', 'document_type', 'email', 'phone')
    search_fields = ('name', 'document', 'email')
    list_filter = ('document_type',)

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('number', 'row', 'column', 'type', 'status', 'get_airplane_model')
    list_filter = ('status', 'type', 'airplane__model')
    search_fields = ('number',)

    def get_airplane_model(self, obj):
        return obj.airplane.model
    get_airplane_model.short_description = 'Airplane Model'

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('reservation_code', 'get_flight_info', 'get_passenger_name', 'status', 'reservation_date', 'price')
    list_filter = ('status', 'reservation_date', 'flight__origin', 'flight__destination')
    search_fields = ('reservation_code', 'passenger__name', 'flight__origin', 'flight__destination')

    def get_flight_info(self, obj):
        return f"{obj.flight.origin} → {obj.flight.destination}"
    get_flight_info.short_description = 'Flight'

    def get_passenger_name(self, obj):
        return obj.passenger.name
    get_passenger_name.short_description = 'Passenger'

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'get_passenger', 'get_flight', 'issue_date', 'status')
    list_filter = ('status', 'issue_date')
    search_fields = ('barcode', 'reservation__reservation_code')

    def get_passenger(self, obj):
        return obj.reservation.passenger.name
    get_passenger.short_description = 'Passenger'

    def get_flight(self, obj):
        flight = obj.reservation.flight
        return f"{flight.origin} → {flight.destination}"
    get_flight.short_description = 'Flight'

@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(DestinationImage)
class DestinationImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'destination', 'image_url')
    search_fields = ('image_url',)
    list_filter = ('destination',)
