from django.template import Library, Node

register = Library()


@register.filter
def subtract(value, arg) -> int:  # Subtract arg from value
    return arg - int(value)
