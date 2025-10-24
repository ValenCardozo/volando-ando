from rest_framework import serializers
from django.contrib.auth.models import User
from app.models import Airplane, Seat, Flight, Reservation, Ticket

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ('id', 'airplane', 'number', 'row', 'column', 'type', 'status')

class AirplaneSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Airplane
        fields = ('id', 'model', 'capacity', 'rows', 'columns', 'seats')

class VueloSerializer(serializers.ModelSerializer):
    airplane = AirplaneSerializer(read_only=True)
    users = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = ('id', 'airplane', 'origin', 'destination', 'departure_time',
                 'arrival_time', 'duration', 'status', 'base_price', 'users')
        depth = 1

    def validate(self, data):
        if 'departure_time' in data and 'arrival_time' in data:
            if data['departure_time'] >= data['arrival_time']:
                raise serializers.ValidationError("El tiempo de salida debe ser anterior al tiempo de llegada")
        return data

class BoletoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'reservation', 'barcode', 'issue_date', 'status')
        read_only_fields = ('barcode', 'issue_date')

class ReservaSerializer(serializers.ModelSerializer):
    passenger = serializers.PrimaryKeyRelatedField(read_only=True)
    ticket = BoletoSerializer(read_only=True)
    flight = VueloSerializer(read_only=True)
    seat = SeatSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ('id', 'flight', 'passenger', 'seat', 'status', 'reservation_date',
                 'price', 'reservation_code', 'ticket')
        read_only_fields = ('reservation_date', 'reservation_code')

    def validate(self, data):
        if 'flight' in data and 'seat' in data:
            # Validar que el asiento pertenece al avión del vuelo
            if data['seat'].airplane != data['flight'].airplane:
                raise serializers.ValidationError(
                    "El asiento seleccionado no pertenece al avión de este vuelo"
                )
            # Validar que el asiento está disponible
            if data['seat'].status != 'available':
                raise serializers.ValidationError(
                    "El asiento seleccionado no está disponible"
                )
        return data