from django import template

register = template.Library()

@register.filter
def absolute(value):
    """Return absolute value (positive number)."""
    try:
        return abs(value)
    except (ValueError, TypeError):
        return value
