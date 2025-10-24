from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views
from .views import RegistroPasajeroView, AvionViewSet

router = DefaultRouter()
router.register(r'aviones', AvionViewSet, basename='avion')

urlpatterns = [
    path('', include(router.urls)),
    path('registro/', RegistroPasajeroView.as_view(), name='registro'),
    path('token/', views.obtain_auth_token, name='token'),
]
