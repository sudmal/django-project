from django import forms
import datetime 

year = str((datetime.date.today() - datetime.timedelta(days=59)).year)

class DateInput(forms.DateInput):
    input_type='date'

class SearchForm(forms.Form):
    search_string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','width':'500px','autofocus':'yes','placeholder': 'Введите текст','id':'tm_search'}), max_length=255)
    start_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':year+'-01-01'}))
    end_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':year+'-12-31'}))
class SearchFormOrg(forms.Form):
    search_string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'yes','placeholder': 'Введите наименование или ЕДРПОУ','id':'org_search'}), max_length=255)
    start_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':year+'-01-01'}))
    end_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':year+'-12-31'}))
 
class FirmDetailForm(forms.Form):
    edrpou = forms.CharField(widget=forms.HiddenInput())