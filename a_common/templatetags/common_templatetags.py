from django.template import Library, Node

register = Library()


@register.filter
def subtract(value, arg) -> int:  # Subtract arg from value
    return arg - int(value)


@register.filter
def digit_of_one(content) -> str:  # Convert to 2-Digit Number
    digit = abs(content) % 10
    if digit == 0:
        return digit + 10
    return digit
