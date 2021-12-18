from django import template
from django.template.defaultfilters import stringfilter
import re

register = template.Library()

@register.filter(name='nbsp_remove', is_safe=True)
@stringfilter
def nbsp_remove(value):
    return re.sub('&nbsp;', '.', value, flags=re.IGNORECASE)