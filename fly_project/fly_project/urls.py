"""
URL configuration for fly_project project.
...
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

from drf_spectacular.views import (
    SpectacularAPIView, 
    SpectacularRedocView, 
    SpectacularSwaggerView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('backoffice/', include('backoffice.urls')),
    path('api/', include('api.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
    path('set_language', set_language, name="set_language"),
    
    # 🎯 Nueva Configuración de Documentación (drf-spectacular)
    # 1. URL para el archivo de esquema OpenAPI (necesario para Swagger/Redoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # 2. URL para Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # 3. URL para Redoc UI
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG == True:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )