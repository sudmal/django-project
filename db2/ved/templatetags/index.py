from django import template
register = template.Library()
""""
if my_list = [['a','b','c'], ['d','e','f']], you can use {{ my_list|index:x|index:y }} in template to get my_list[x][y]

It works fine with "for"

{{ my_list|index:forloop.counter0 }}
"""



@register.filter
def index(indexable, i):
    return indexable[i]