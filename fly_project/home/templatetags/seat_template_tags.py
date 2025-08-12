from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Filter to access dictionary items by key in templates
    Usage: {{ dictionary|get_item:key }}
    """
    return dictionary.get(key)