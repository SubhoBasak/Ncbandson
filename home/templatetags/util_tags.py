from django import template

register = template.Library()


@register.simple_tag()
def mul_on_temp(qty, unit_price, *args, **kwargs):
    return qty * unit_price