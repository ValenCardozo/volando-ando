from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Airplane(models.Model):
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    rows = models.PositiveIntegerField()
    columns = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.model} (Capacity: {self.capacity})"

class Flight(models.Model):
    STATUSES = [
        ("scheduled", "Scheduled"),
        ("in_flight", "In flight"),
        ("completed", "Completed"),
        ("canceled", "Canceled"),
    ]
    airplane = models.ForeignKey(Airplane, on_delete=models.PROTECT, related_name="flights")
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    duration = models.DurationField()
    status = models.CharField(max_length=20, choices=STATUSES, default="scheduled")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    users = models.ManyToManyField(User, related_name="managed_flights", blank=True)

    def __str__(self):
        return f"Flight {self.id} - {self.origin} to {self.destination}"

class Passenger(models.Model):
    DOCUMENT_TYPES = [
        ("DNI", "DNI"),
        ("PASSPORT", "Passport"),
        ("OTHER", "Other"),
    ]
    name = models.CharField(max_length=100)
    document = models.CharField(max_length=30, unique=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    birth_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.document})"

class Seat(models.Model):
    SEAT_TYPES = [
        ("economy", "Economy"),
        ("premium", "Premium"),
        ("business", "Business"),
    ]
    SEAT_STATUSES = [
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("occupied", "Occupied"),
    ]
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE, related_name="seats")
    number = models.CharField(max_length=10)
    row = models.PositiveIntegerField()
    column = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=SEAT_TYPES)
    status = models.CharField(max_length=20, choices=SEAT_STATUSES, default="available")

    class Meta:
        unique_together = ("airplane", "number")

    def __str__(self):
        return f"Seat {self.number} ({self.type}) - {self.airplane.model}"

class Reservation(models.Model):
    STATUS_OPTIONS = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("canceled", "Canceled"),
    ]
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name="reservations")
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name="reservations")
    seat = models.OneToOneField(Seat, on_delete=models.PROTECT, related_name="reservation")
    status = models.CharField(max_length=20, choices=STATUS_OPTIONS, default="pending")
    reservation_date = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    reservation_code = models.CharField(max_length=20, unique=True)

    class Meta:
        unique_together = ("flight", "passenger")

    def __str__(self):
        return f"Reservation {self.reservation_code} - Flight {self.flight.id} - {self.passenger.name}"

class Ticket(models.Model):
    STATUS_OPTIONS = [
        ("issued", "Issued"),
        ("canceled", "Canceled"),
    ]
    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE, related_name="ticket")
    barcode = models.CharField(max_length=50, unique=True)
    issue_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_OPTIONS, default="issued")

    def __str__(self):
        return f"Ticket {self.barcode} - Reservation {self.reservation.reservation_code}"

class Destination(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class DestinationImage(models.Model):
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='images')
    image_url = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.destination.name} - {self.image_url}"
