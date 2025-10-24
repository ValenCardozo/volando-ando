from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from app.models import Airplane, Seat
from .serializers import UserSerializer, AirplaneSerializer, SeatSerializer

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
