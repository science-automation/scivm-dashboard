from django import template
from django.template.defaultfilters import stringfilter
from django.utils.translation import ugettext as _
from datetime import datetime

register = template.Library()

@register.filter()
def split(value, arg):
    return value.split(arg)
