import uuid
from rest_framework.exceptions import ValidationError
from .models import Flight, Reservation, Ticket, Seat
from django.utils import timezone

class ReservaService:
    def crear_reserva(self, data, user):
        """
        Crear una nueva reserva con validaciones de negocio
        """
        flight = data['flight']
        seat = data['seat']

        # Validar que el vuelo está programado
        if flight.status != 'scheduled':
            raise ValidationError("Solo se pueden hacer reservas para vuelos programados")

        # Validar que el asiento pertenece al avión del vuelo
        if seat.airplane != flight.airplane:
            raise ValidationError("El asiento no pertenece al avión de este vuelo")

        # Validar que el asiento está disponible
        if seat.status != 'available':
            raise ValidationError("El asiento no está disponible")

        # Generar código de reserva único
        reservation_code = str(uuid.uuid4())[:8].upper()

        # Crear la reserva
        reserva = Reservation.objects.create(
            flight=flight,
            passenger=user,
            seat=seat,
            status='pending',
            price=flight.base_price,  # Aquí podrías aplicar lógica de precios
            reservation_code=reservation_code
        )

        # Actualizar estado del asiento
        seat.status = 'reserved'
        seat.save()

        return reserva

    def cambiar_estado_reserva(self, reserva, nuevo_estado):
        """
        Cambiar el estado de una reserva
        """
        estados_validos = [choice[0] for choice in Reservation.STATUS_OPTIONS]
        if nuevo_estado not in estados_validos:
            raise ValidationError(f"Estado no válido. Opciones: {estados_validos}")

        # Validar transiciones de estado permitidas
        if reserva.status == 'pending' and nuevo_estado not in ['confirmed', 'canceled']:
            raise ValidationError("Una reserva pendiente solo puede ser confirmada o cancelada")
        elif reserva.status == 'confirmed' and nuevo_estado != 'canceled':
            raise ValidationError("Una reserva confirmada solo puede ser cancelada")
        elif reserva.status == 'canceled':
            raise ValidationError("No se puede cambiar el estado de una reserva cancelada")

        # Actualizar estado de la reserva
        reserva.status = nuevo_estado
        reserva.save()

        # Actualizar estado del asiento
        if nuevo_estado == 'confirmed':
            reserva.seat.status = 'occupied'
        elif nuevo_estado == 'canceled':
            reserva.seat.status = 'available'
        reserva.seat.save()

        return reserva

    def generar_boleto(self, reserva):
        """
        Generar un boleto para una reserva confirmada
        """
        if reserva.status != 'confirmed':
            raise ValidationError("Solo se pueden generar boletos para reservas confirmadas")

        if hasattr(reserva, 'ticket'):
            raise ValidationError("Ya existe un boleto para esta reserva")

        # Generar código de barras único
        barcode = f"TKT-{str(uuid.uuid4())[:12].upper()}"

        # Crear el boleto
        ticket = Ticket.objects.create(
            reservation=reserva,
            barcode=barcode,
            status='issued'
        )

        return ticket


class FlightService:
    def create_flight(self, data):
        """
        Crear un nuevo vuelo con validaciones de negocio
        """
        # Validar que el avión existe y tiene capacidad
        airplane = data.get('airplane')
        if not airplane or not airplane.capacity > 0:
            raise ValidationError("Se requiere un avión válido con capacidad disponible")

        # Validar fechas
        departure_time = data.get('departure_time')
        arrival_time = data.get('arrival_time')
        if departure_time and arrival_time and departure_time >= arrival_time:
            raise ValidationError("El tiempo de salida debe ser anterior al tiempo de llegada")

        # Validar estado inicial
        status = data.get('status', 'scheduled')
        if status not in [s[0] for s in Flight.STATUSES]:
            raise ValidationError(f"Estado no válido. Opciones permitidas: {[s[0] for s in Flight.STATUSES]}")

        return Flight.objects.create(**data)

    def update_flight(self, flight, data):
        """
        Actualizar un vuelo existente con validaciones de negocio
        """
        # No permitir cambios en vuelos completados o cancelados
        if flight.status in ['completed', 'canceled']:
            raise ValidationError("No se pueden modificar vuelos completados o cancelados")

        # Validar cambio de estado
        if 'status' in data:
            new_status = data['status']
            if new_status not in [s[0] for s in Flight.STATUSES]:
                raise ValidationError(f"Estado no válido. Opciones permitidas: {[s[0] for s in Flight.STATUSES]}")

            # Validar transición de estado
            if flight.status == 'scheduled' and new_status not in ['in_flight', 'canceled']:
                raise ValidationError("Un vuelo programado solo puede pasar a en vuelo o cancelado")
            elif flight.status == 'in_flight' and new_status not in ['completed']:
                raise ValidationError("Un vuelo en progreso solo puede pasar a completado")

        # Actualizar campos
        for key, value in data.items():
            setattr(flight, key, value)
        flight.save()
        return flight

    def delete_flight(self, flight):
        """
        Eliminar un vuelo con validaciones de negocio
        """
        if flight.status not in ['scheduled', 'canceled']:
            raise ValidationError("Solo se pueden eliminar vuelos programados o cancelados")
        
        # Verificar si hay reservas asociadas
        if flight.reservations.exists():
            raise ValidationError("No se puede eliminar un vuelo con reservas existentes")
            
        flight.delete()