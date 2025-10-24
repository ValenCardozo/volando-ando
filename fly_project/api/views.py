from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from app.models import Airplane, Seat, Flight, Reservation, Ticket
from app.services import FlightService, ReservaService
from .permissions import IsAdminUser
from .serializers import (
    UserSerializer, AirplaneSerializer, SeatSerializer, VueloSerializer,
    ReservaSerializer, BoletoSerializer, PassengerSerializer
)

class RegistroPasajeroView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AvionViewSet(ReadOnlyModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer

    @action(detail=True, methods=['get'])
    def layout_asientos(self, request, pk=None):
        instance = self.get_object()
        asientos = Seat.objects.filter(airplane=instance)
        serializer = SeatSerializer(asientos, many=True)
        return Response(serializer.data)

class VueloViewSet(ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = VueloSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['origin', 'destination', 'departure_time', 'status']

    @action(detail=True, methods=['get'], permission_classes=[IsAdminUser])
    def pasajeros(self, request, pk=None):
        vuelo = self.get_object()
        reservas = vuelo.reservations.filter(status='confirmed')
        pasajeros = [reserva.passenger for reserva in reservas]
        serializer = PassengerSerializer(pasajeros, many=True)
        return Response({
            'total_pasajeros': len(pasajeros),
            'pasajeros': serializer.data
        })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.flight_service = FlightService()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        return self.flight_service.create_flight(serializer.validated_data)

    def perform_update(self, serializer):
        return self.flight_service.update_flight(self.get_object(), serializer.validated_data)

    def perform_destroy(self, instance):
        self.flight_service.delete_flight(instance)

class ReservaViewSet(ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'flight']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.reserva_service = ReservaService()

    def get_queryset(self):
        return Reservation.objects.filter(passenger__email=self.request.user.email)

    def perform_create(self, serializer):
        return self.reserva_service.crear_reserva(serializer.validated_data, self.request.user)

    @action(detail=True, methods=['post'])
    def cambiar_estado(self, request, pk=None):
        reserva = self.get_object()
        nuevo_estado = request.data.get('status')
        if not nuevo_estado:
            return Response(
                {'error': 'Debe proporcionar el nuevo estado'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            reserva = self.reserva_service.cambiar_estado_reserva(reserva, nuevo_estado)
            serializer = self.get_serializer(reserva)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def generar_boleto(self, request, pk=None):
        reserva = self.get_object()
        try:
            ticket = self.reserva_service.generar_boleto(reserva)
            serializer = BoletoSerializer(ticket)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
