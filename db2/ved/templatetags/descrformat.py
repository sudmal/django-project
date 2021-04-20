from django import template

register = template.Library()
@register.filter(is_safe=True,needs_autoescape=False)
def descrformat(str1):
    st=''
    result=''
    
    if str1.find(";")>=0:
        str1=str1.replace(";",";<br>")
    if str1.find(":")>=0:
        str1=str1.replace(":",":<br>")
    return(str1)


