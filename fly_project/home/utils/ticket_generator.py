import os
import qrcode
import random
import string
from io import BytesIO
from datetime import datetime
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from app.models import Ticket, Reservation

def generate_barcode():
    """Generate a unique barcode for the ticket"""
    barcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    while Ticket.objects.filter(barcode=barcode).exists():
        barcode = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    return barcode

def create_qr_code(data):
    """Create a QR code image from data"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to BytesIO
    buffer = BytesIO()
    img.save(buffer)
    buffer.seek(0)
    
    return buffer

def generate_ticket_pdf(reservation):
    """Generate a PDF ticket for a reservation"""
    # Create directory if it doesn't exist
    media_path = os.path.join(settings.MEDIA_ROOT, 'tickets')
    os.makedirs(media_path, exist_ok=True)
    
    # Generate filename
    filename = f"ticket_{reservation.reservation_code}.pdf"
    filepath = os.path.join(media_path, filename)
    
    # Create PDF
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create a custom style for the title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        alignment=1,
        spaceAfter=0.3*inch,
        textColor=colors.navy
    )
    
    # Create a custom style for the subtitle
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Heading2'],
        alignment=1,
        spaceAfter=0.2*inch,
        textColor=colors.darkblue
    )
    
    # Create QR code with reservation details
    qr_data = f"FLIGHT: {reservation.flight.id}\nRESERVATION: {reservation.reservation_code}\nPASSENGER: {reservation.passenger.name}\nSEAT: {reservation.seat.number}"
    qr_buffer = create_qr_code(qr_data)
    qr_image = Image(qr_buffer, width=2*inch, height=2*inch)
    
    # Create content
    content = []
    
    # Add title
    content.append(Paragraph("VOLANDO ANDO", title_style))
    content.append(Paragraph("Boleto Electrónico", subtitle_style))
    content.append(Spacer(1, 0.2*inch))
    
    # Add flight information
    flight_data = [
        ["Vuelo:", f"{reservation.flight.id}"],
        ["Origen:", f"{reservation.flight.origin}"],
        ["Destino:", f"{reservation.flight.destination}"],
        ["Fecha de salida:", f"{reservation.flight.departure_time.strftime('%d/%m/%Y')}"],
        ["Hora de salida:", f"{reservation.flight.departure_time.strftime('%H:%M')}"],
        ["Fecha de llegada:", f"{reservation.flight.arrival_time.strftime('%d/%m/%Y')}"],
        ["Hora de llegada:", f"{reservation.flight.arrival_time.strftime('%H:%M')}"],
    ]
    
    flight_table = Table(flight_data, colWidths=[1.5*inch, 4*inch])
    flight_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    
    content.append(flight_table)
    content.append(Spacer(1, 0.2*inch))
    
    # Add passenger information
    passenger_title = ParagraphStyle(
        'PassengerTitle',
        parent=styles['Heading3'],
        textColor=colors.darkblue
    )
    content.append(Paragraph("Información del Pasajero", passenger_title))
    content.append(Spacer(1, 0.1*inch))
    
    passenger_data = [
        ["Nombre:", f"{reservation.passenger.name}"],
        ["Documento:", f"{reservation.passenger.document} ({reservation.passenger.document_type})"],
        ["Email:", f"{reservation.passenger.email}"],
    ]
    
    passenger_table = Table(passenger_data, colWidths=[1.5*inch, 4*inch])
    passenger_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    
    content.append(passenger_table)
    content.append(Spacer(1, 0.2*inch))
    
    # Add ticket information
    ticket_title = ParagraphStyle(
        'TicketTitle',
        parent=styles['Heading3'],
        textColor=colors.darkblue
    )
    content.append(Paragraph("Detalles del Boleto", ticket_title))
    content.append(Spacer(1, 0.1*inch))
    
    # Get or create ticket
    try:
        ticket = reservation.ticket
    except Ticket.DoesNotExist:
        barcode = generate_barcode()
        ticket = Ticket.objects.create(
            reservation=reservation,
            barcode=barcode,
            status="issued"
        )
    
    ticket_data = [
        ["Código de Reserva:", f"{reservation.reservation_code}"],
        ["Asiento:", f"{reservation.seat.number}"],
        ["Clase:", f"{reservation.seat.get_type_display()}"],
        ["Precio:", f"${reservation.price}"],
        ["Fecha de emisión:", f"{ticket.issue_date.strftime('%d/%m/%Y %H:%M')}"],
        ["Código de boleto:", f"{ticket.barcode}"],
    ]
    
    ticket_table = Table(ticket_data, colWidths=[1.5*inch, 4*inch])
    ticket_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.darkblue),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    
    content.append(ticket_table)
    content.append(Spacer(1, 0.3*inch))
    
    # Add QR code
    content.append(Paragraph("Escanee este código QR en el mostrador de embarque", styles['Italic']))
    content.append(Spacer(1, 0.1*inch))
    content.append(qr_image)
    
    # Add disclaimer
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Italic'],
        fontSize=8,
        textColor=colors.grey
    )
    disclaimer_text = """
    Este boleto electrónico es personal e intransferible. Preséntese en el aeropuerto al menos 2 horas antes 
    para vuelos nacionales y 3 horas para vuelos internacionales. Volando Ando no se responsabiliza por 
    cambios de último momento. Por favor, verifique el estado de su vuelo antes de dirigirse al aeropuerto.
    """
    content.append(Spacer(1, 0.3*inch))
    content.append(Paragraph(disclaimer_text, disclaimer_style))
    
    # Build PDF
    doc.build(content)
    
    # Return relative path for storage in database
    relative_path = os.path.join('tickets', filename)
    return relative_path