from django import template

register = template.Library()
@register.filter(is_safe=True,needs_autoescape=False)
def bold_in_quotes(str1):
    st=''
    result=''
    
    # Заменяем все возможные варианты кавычек на простые двойные
    if str1.find("«")>=0 and str1.find("»")>=0:
        str1=str1.replace("«","\"")
        str1=str1.replace("»","\"")
    if str1.find("”")>=0 and str1.find("“")>=0:
        str1=str1.replace("”","\"")
        str1=str1.replace("“","\"")
    if str1.find("'")>=0:
        str1=str1.replace("'","\"")


    if str1.find("\"")>=0 :
        st=str1.split("\"")

        if len(st[0])>0:
            result='<span style="cursor: help; font-size: 16px !important; font-weight: bold;" data-toggle="tooltip" data-placement="right" title="'+st[0]+'">'
    #        result="<small class=\"text-muted\">"+st[0]+"</small><br><span class=\"font-weight-bold\">"
            for s in st[1:]:
                result=result+s
            result=result+"</span>"
        else:
            result="<span style=\"font-size: 16px !important; font-weight: bold;\">"+str1+"</span>"     
    else:
        result="<span style=\"font-size: 16px !important; font-weight: bold;\">"+str1+"</span>"
    return(result)


