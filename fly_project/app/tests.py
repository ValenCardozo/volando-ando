
from django.test import TestCase
from app.models import Airplane
from app.models import Airplane, Passenger, Seat

class AirplaneModelTest(TestCase):
	def test_create_airplane(self):
		airplane = Airplane.objects.create(model="Boeing 737", capacity=180, rows=30, columns=6)
		self.assertEqual(airplane.model, "Boeing 737")
		self.assertEqual(airplane.capacity, 180)
		self.assertEqual(airplane.rows, 30)
		self.assertEqual(airplane.columns, 6)
		self.assertEqual(str(airplane), "Boeing 737 (Capacity: 180)")

class PassengerModelTest(TestCase):
	def test_create_passenger(self):
		passenger = Passenger.objects.create(
			name="Juan Perez",
			document="12345678",
			document_type="DNI",
			email="juan@example.com",
			phone="123456789",
			birth_date="1990-01-01"
		)
		self.assertEqual(passenger.name, "Juan Perez")
		self.assertEqual(passenger.document, "12345678")
		self.assertEqual(str(passenger), "Juan Perez (12345678)")

class SeatModelTest(TestCase):
	def test_create_seat(self):
		airplane = Airplane.objects.create(model="Airbus A320", capacity=150, rows=25, columns=6)
		seat = Seat.objects.create(airplane=airplane, number="1A", row=1, column=1, type="economy", status="available")
		self.assertEqual(seat.number, "1A")
		self.assertEqual(seat.type, "economy")
		self.assertEqual(seat.status, "available")
		self.assertEqual(str(seat), "Seat 1A (economy) - Airbus A320")

class AirplaneModelTest(TestCase):
	def test_create_airplane(self):
		airplane = Airplane.objects.create(model="Boeing 737", capacity=180, rows=30, columns=6)
		self.assertEqual(airplane.model, "Boeing 737")
		self.assertEqual(airplane.capacity, 180)
		self.assertEqual(airplane.rows, 30)
		self.assertEqual(airplane.columns, 6)
