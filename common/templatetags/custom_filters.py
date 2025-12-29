# common/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter(name='get_attr')
def get_attr(obj, attr):
    return getattr(obj, attr, '')