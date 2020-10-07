from django import template

register = template.Library()
@register.filter(is_safe=True,needs_autoescape=False)
def bold_in_quotes(str1):
    st=''
    result=''

    if str1.find("«")>=0 and str1.find("»")>=0:
        str1=str1.replace("«","\"")
        str1=str1.replace("»","\"")
    if str1.find("”")>=0 and str1.find("“")>=0:
        str1=str1.replace("”","\"")
        str1=str1.replace("“","\"")

    if str1.find("'")>=0:
        st=str1.split("'")
        result="<small class=\"text-muted\">"+st[0]+"</small> <span class=\"font-weight-bold\">\""
        for s in st[1:]:
            result=result+s
        result=result+"\"</span>"    
    elif str1.find("\"")>=0:
        st=str1.split("\"")
        result="<small class=\"text-muted\">"+st[0]+"</small> <span class=\"font-weight-bold\">\""
        for s in st[1:]:
            result=result+s
        result=result+"\"</span>" 
    else:
        result=str1
    return(result)


