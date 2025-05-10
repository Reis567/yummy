from django import template

register = template.Library()

@register.filter(name='abs')
def absolute(value):
    """Retorna o valor absoluto de um número"""
    return abs(value)