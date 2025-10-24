from rest_framework import serializers
from django.contrib.auth.models import User
from app.models import Airplane, Seat

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