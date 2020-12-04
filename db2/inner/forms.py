from django import forms
from .models import NlReestr
from django.db.models import Max
import datetime 

year = str((datetime.date.today() - datetime.timedelta(days=59)).year)
db_max_date=str(NlReestr.objects.filter(ordering_date__range=[str(year)+'-01-01', str(year)+'-12-31']).aggregate(Max('ordering_date'))['ordering_date__max'])

class SearchFormOrg(forms.Form):
    search_string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'yes','placeholder': 'Введите наименование или ЕДРПОУ','id':'org_search'}), max_length=255)
    #start_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':year+'-01-01'}))
    #end_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':db_max_date}))