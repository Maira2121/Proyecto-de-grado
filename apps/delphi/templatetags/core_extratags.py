from django import template
import re

from django.contrib.auth.forms import ReadOnlyPasswordHashWidget
from django.forms.forms import BoundField
from django.forms.widgets import CheckboxInput, RadioSelect, CheckboxSelectMultiple
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='add_css')
def addcss(field, css):
    """
    :param field: Field of a Form rendered in a django template
    :param css: css class to add to the field
    :return: a string rendered for the field with the new class
    """
    attrs = field.form.fields.get(field.name).widget.attrs
    classess = (attrs['class']+' ' if 'class' in attrs.keys() else '')+css
    return field.as_widget(attrs={"class":classess})

@register.filter(name='add_value')
def addvalue(field, value):
    """
    :param field: Field of a Form rendered in a django template
    :param value: value to add to the field
    :return: a string rendered for the field with the new value
    """
    return field.as_widget(attrs={"value":value})

@register.filter(name='add_data')
def add_data(field, value):
    """
    :param field: Field of a Form rendered in a django template
    :param value: data-id to add to the field
    :return: a string rendered for the field with the new value
    """
    return field.as_widget(attrs={"data-id":value})

@register.filter(name='index')
def get_at_index(list, index):
    """
    :param list: Python list
    :param index: given index of List
    :return: object at the index given in the list
    """
    return list[index]

@register.filter
def get_range( value ):
  """
    Filter - returns a list containing range made from given value
    Usage (in template):

    <ul>{% for i in 3|get_range %}
      <li>{{ i }}. Do something</li>
    {% endfor %}</ul>

    Results with the HTML:
    <ul>
      <li>0. Do something</li>
      <li>1. Do something</li>
      <li>2. Do something</li>
    </ul>

    Instead of 3 one may use the variable set in the views
  """
  return range( value )

@register.filter()
def to_int(value):
    return int(value)

@register.filter(name='is_checkbox')
def is_checkbox(value):
    return isinstance(value, CheckboxInput) or isinstance(value, CheckboxSelectMultiple)

@register.filter(name='is_radio')
def is_radio(value):
    return isinstance(value, RadioSelect)

@register.filter(name='is_readonly_widget')
def is_readonly_widget(value):
    return isinstance(value, ReadOnlyPasswordHashWidget) or isinstance(value, ReadOnlyPasswordHashWidget)

@register.filter(name='type')
def type_of(value):
    return type(value).__name__