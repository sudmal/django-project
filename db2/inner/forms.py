from django import forms
from .models import NlReestr
from django.db.models import Max
import datetime 
from django.db.models.functions import ExtractYear


reestr_years = NlReestr.objects.extra(select={'year':"extract(year from ordering_date)"}).distinct().values('year').order_by()
print(reestr_years)

class DateInput(forms.DateInput):
    input_type='date'

year = str((datetime.date.today() - datetime.timedelta(days=59)).year)
db_max_date=str(NlReestr.objects.filter(ordering_date__range=[str(year)+'-01-01', str(year)+'-12-31']).aggregate(Max('ordering_date'))['ordering_date__max'])

class SearchFormOrg(forms.Form):
    search_string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'yes','placeholder': 'Введите наименование или ЕДРПОУ','id':'org_search'}), max_length=255)
class DatesStartEndForm(forms.Form):
    start_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':year+'-01-01'}))
    end_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':db_max_date}))

class NlYearSelectForm(forms.Form):
    CHOICES = [('2017','2017'), ('2018','2018'), ('2019','2019'), ('2020','2020')]
    selected_year = forms.ChoiceField(label='', choices=CHOICES,initial=year, widget=forms.Select(attrs={'class':'form-control'}))
