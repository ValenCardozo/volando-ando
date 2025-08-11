from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def times(number):
    """Genera un rango de números para iterar"""
    try:
        return range(1, int(number) + 1)
    except (ValueError, TypeError):
        return range(0)

@register.filter
def to_letter(number):
    """Convierte un número a una letra (1=A, 2=B, etc.)"""
    try:
        num = int(number)
        return chr(64 + num)  # ASCII: A=65, B=66, etc.
    except (ValueError, TypeError):
        return ''

@register.filter
def get_seat(seats, seat_number):
    """Obtiene un asiento del queryset por su número"""
    for seat in seats:
        if seat.number == seat_number:
            return seat
    return None

@register.filter
def multiply(val1, val2):
    """Multiplica dos valores"""
    try:
        return int(val1) * int(val2)
    except (ValueError, TypeError):
        return 0

@register.filter
def seat_status_color(status):
    """Devuelve un color según el estado del asiento"""
    if status == 'available':
        return 'success'
    elif status == 'reserved':
        return 'warning'
    elif status == 'occupied':
        return 'danger'
    return 'secondary'

@register.filter
def seat_type_color(seat_type):
    """Devuelve un color según el tipo de asiento"""
    if seat_type == 'economy':
        return 'primary'
    elif seat_type == 'premium':
        return 'info'
    elif seat_type == 'business':
        return 'success'
    return 'secondary'