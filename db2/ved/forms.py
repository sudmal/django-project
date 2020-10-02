from django import forms
import datetime 

year = str((datetime.date.today() - datetime.timedelta(days=59)).year)

class DateInput(forms.DateInput):
    input_type='date'
class SearchForm(forms.Form):
    search_string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','width':'500px','autofocus':'yes','placeholder': 'Введите текст'}), max_length=100)
    start_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':year+'-01-01'}))
    end_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':year+'-12-31'}))

 
class FirmDetailForm(forms.Form):
    edrpou = forms.CharField(widget=forms.HiddenInput())