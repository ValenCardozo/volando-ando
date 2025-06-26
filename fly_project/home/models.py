from django.db import models
from django.contrib.auth.models import User

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
