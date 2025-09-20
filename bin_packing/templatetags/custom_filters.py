from django import template
from django.utils.html import format_html

register = template.Library()


@register.filter(name='div')
def div(num1, num2):
    return round(num1/num2, 2)
