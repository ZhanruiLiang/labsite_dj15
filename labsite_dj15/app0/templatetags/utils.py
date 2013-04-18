from django import template

register = template.Library()

@register.filter
def getkey(value, arg):
    return value.get(arg, '')
