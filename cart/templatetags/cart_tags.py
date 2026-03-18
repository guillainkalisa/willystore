from django import template

register = template.Library()

@register.filter
def is_equal(value, arg):
    """
    Returns True if value equals arg (after converting both to string).
    This bypasses IDE formatting issues with Django's == operator.
    """
    return str(value) == str(arg)
