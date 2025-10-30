from rest_framework.test import APITestCase
from django.urls import reverse
from app.models import Airplane, Seat, Flight, Passenger
from django.utils import timezone
from django.contrib.auth.models import User
import datetime

class ReservaVueloIntegrationTest(APITestCase):
	def setUp(self):
		print("Creando usuario de prueba")
		self.user = User.objects.create_user(username="testuser", password="testpass")
		print("Usuario:", self.user)
		self.client.force_authenticate(user=self.user)
		print("Creando avión")
		self.airplane = Airplane.objects.create(model="Boeing 737", capacity=180, rows=30, columns=6)
		print("Avión:", self.airplane)
		print("Creando asiento")
		self.seat = Seat.objects.create(airplane=self.airplane, number="1A", row=1, column=1, type="economy", status="available")
		print("Asiento:", self.seat)
		print("Creando vuelo")
		self.flight = Flight.objects.create(
			airplane=self.airplane,
			origin="Buenos Aires",
			destination="Córdoba",
			departure_time=timezone.now() + datetime.timedelta(days=1),
			arrival_time=timezone.now() + datetime.timedelta(days=1, hours=1),
			duration=datetime.timedelta(hours=1),
			status="scheduled",
			base_price=1000
		)
		print("Vuelo:", self.flight)
		print("Creando pasajero")
		self.passenger = Passenger.objects.create(
			name="Pela Perez",
			document="12345678",
			document_type="DNI",
			email="pela@example.com",
			phone="123456789",
			birth_date="1990-01-01"
		)
		print("Pasajero:", self.passenger)

	def test_flujo_reserva_vuelo(self):
		print("\n-------------------------------------------------")
		print("\nTest: Flujo completo de reserva de vuelo")
		url = reverse('reserva-list')
		data = {
			"flight": self.flight.id,
			"passenger": self.passenger.id,
			"seat": self.seat.id,
			"price": 1000
		}
		print(f"Enviando POST a {url} con datos: {data}")
		response = self.client.post(url, data, format='json')
		print(f"Respuesta del endpoint: {response.status_code} - {response.data}")
		self.assertEqual(response.status_code, 201)

		self.assertIn('flight', response.data)
		self.assertIn('seat', response.data)
		self.assertIn('price', response.data)
		self.assertEqual(response.data['flight'], self.flight.id)
		self.assertEqual(response.data['seat'], self.seat.id)
		self.assertEqual(response.data['price'], '1000.00')

	def test_no_permite_reservar_asiento_ocupado(self):
		print("\n-------------------------------------------------")
		print("\nTest: No permite reservar un asiento ya ocupado")
		# Crear primera reserva (ocupa el asiento)
		url = reverse('reserva-list')
		data1 = {
			"flight": self.flight.id,
			"passenger": self.passenger.id,
			"seat": self.seat.id,
			"price": 1000
		}

		print(f"Reservando asiento para primer pasajero: {data1}")

		response1 = self.client.post(url, data1, format='json')

		print(f"Respuesta 1: {response1.status_code} - {response1.data}")
		self.assertEqual(response1.status_code, 201)

		passenger2 = Passenger.objects.create(
			name="Segundo Pasajero",
			document="87654321",
			document_type="DNI",
			email="segundo@example.com",
			phone="987654321",
			birth_date="1992-02-02"
		)
		print("Segundo pasajero:", passenger2)

		data2 = {
			"flight": self.flight.id,
			"passenger": passenger2.id,
			"seat": self.seat.id,
			"price": 1000
		}

		print(f"Intentando reservar asiento ya ocupado para segundo pasajero: {data2}")

		response2 = self.client.post(url, data2, format='json')

		print(f"Respuesta 2: {response2.status_code} - {response2.data}")

		self.assertEqual(response2.status_code, 400)
		self.assertIn('non_field_errors', response2.data)
		self.assertIn('no está disponible', str(response2.data['non_field_errors']))

	def test_pasajero_no_puede_reservar_dos_veces_mismo_vuelo(self):
		from django.db import IntegrityError
		print("\n-------------------------------------------------")
		print("\nTest: Un pasajero no puede tener más de una reserva por vuelo")
		# Crear primer asiento y reserva
		seat2 = Seat.objects.create(airplane=self.airplane, number="1B", row=1, column=2, type="economy", status="available")
		url = reverse('reserva-list')
		data1 = {
			"flight": self.flight.id,
			"passenger": self.passenger.id,
			"seat": self.seat.id,
			"price": 1000
		}
		response1 = self.client.post(url, data1, format='json')
		print(f"Primera reserva: {response1.status_code} - {response1.data}")
		self.assertEqual(response1.status_code, 201)
		# Intentar reservar otro asiento para el mismo pasajero y vuelo
		data2 = {
			"flight": self.flight.id,
			"passenger": self.passenger.id,
			"seat": seat2.id,
			"price": 1000
		}
		try:
			response2 = self.client.post(url, data2, format='json')
			print(f"Segunda reserva (debería fallar): {response2.status_code} - {response2.data}")
			self.fail("Se esperaba IntegrityError pero la API devolvió una respuesta")
		except IntegrityError as e:
			print(f"IntegrityError capturado correctamente: {e}")

	def test_estado_asiento_consistente_con_reserva_y_cancelacion(self):
		print("\n-------------------------------------------------")
		print("\nTest: Estado de asiento consistente con reserva y cancelación")
		url = reverse('reserva-list')
		data = {
			"flight": self.flight.id,
			"passenger": self.passenger.id,
			"seat": self.seat.id,
			"price": 1000
		}
		response = self.client.post(url, data, format='json')
		print(f"Reserva creada: {response.status_code} - {response.data}")
		self.assertEqual(response.status_code, 201)

		self.seat.refresh_from_db()
		print(f"Estado del asiento tras reservar: {self.seat.status}")
		self.assertIn(self.seat.status, ['reserved', 'occupied'])

		reserva_id = response.data.get('id')
		if reserva_id:
			cancel_url = reverse('reserva-detail', args=[reserva_id])
			print(f"Cancelando reserva con PATCH a {cancel_url}")
			cancel_response = self.client.patch(cancel_url, {"status": "canceled"}, format='json')
			print(f"Respuesta cancelación: {cancel_response.status_code} - {cancel_response.data}")
			self.assertIn(cancel_response.status_code, [200, 202])
			self.seat.refresh_from_db()
			print(f"Estado del asiento tras cancelar: {self.seat.status}")
			self.assertEqual(self.seat.status, 'available')
		else:
			print("No se pudo obtener el id de la reserva para cancelar.")

	def test_pasajero_documento_unico(self):
		print("\n-------------------------------------------------")
		print("\nTest: Documento de pasajero debe ser único")

		try:
			Passenger.objects.create(
				name="Repetido",
				document="12345678",
				document_type="DNI",
				email="otro@example.com",
				phone="000000000",
				birth_date="1995-05-05"
			)
			self.fail("Se permitió crear un pasajero con documento duplicado")
		except Exception as e:
			print(f"Error esperado: {e}")
			self.assertIn('unique', str(e).lower())