from django.views import View
from django.http import HttpResponse, Http404, FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from app.models import Reservation, Ticket
from django.conf import settings
import os
import random
import string
from .utils.ticket_generator import generate_ticket_pdf

class DownloadTicketView(LoginRequiredMixin, View):
    def get(self, request, reservation_id):
        # Obtener la reserva
        reservation = get_object_or_404(Reservation, id=reservation_id, passenger__email=request.user.email)
        
        # Verificar si existe un ticket asociado
        try:
            ticket = reservation.ticket
        except Ticket.DoesNotExist:
            # Si no existe, generar uno nuevo
            barcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
            while Ticket.objects.filter(barcode=barcode).exists():
                barcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
                
            ticket = Ticket.objects.create(
                reservation=reservation,
                barcode=barcode,
                status="issued"
            )
        
        # Generar o recuperar el PDF del ticket
        ticket_filename = f"ticket_{reservation.reservation_code}.pdf"
        ticket_filepath = os.path.join(settings.MEDIA_ROOT, 'tickets', ticket_filename)
        
        # Si el archivo no existe, generarlo
        if not os.path.exists(ticket_filepath):
            # Asegurar que el directorio existe
            os.makedirs(os.path.join(settings.MEDIA_ROOT, 'tickets'), exist_ok=True)
            
            # Generar el PDF
            generate_ticket_pdf(reservation)
        
        # Verificar que el archivo exista después de intentar generarlo
        if not os.path.exists(ticket_filepath):
            raise Http404("El boleto no se pudo generar.")
            
        # Abrir el archivo y devolverlo como respuesta
        try:
            return FileResponse(
                open(ticket_filepath, 'rb'),
                content_type='application/pdf',
                as_attachment=True,
                filename=ticket_filename
            )
        except FileNotFoundError:
            raise Http404("El archivo del boleto no se encontró en el servidor.")