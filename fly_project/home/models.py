from django.db import models
from django.contrib.auth.models import User

class Airplane(models.Model):
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    rows = models.PositiveIntegerField()
    columns = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.model} (Capacity: {self.capacity})"
