from django import forms
from .models import NlReestr
from django.db.models import Max
import datetime 
from django.db.models.functions import ExtractYear
from django.forms.fields import BooleanField


reestr_years = NlReestr.objects.extra(select={'year':"extract(year from ordering_date)"}).distinct().values('year').order_by()


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

class FirmTypeSelectForm(forms.Form):
    f_horeca = BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-control-input','id':'f_horeca', 'checked' : ''}))
    f_eat = BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-control-input','id':'f_eat', 'checked' : ''}))
    f_pack = BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-control-input','id':'f_pack', 'checked' : ''}))
    f_other = BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-control-input','id':'f_other'}))
    def __init__(self, *args, **kwargs):
        super(FirmTypeSelectForm, self).__init__(*args, **kwargs)
        self.fields['f_horeca'].initial = True
        self.fields['f_eat'].initial = True
        self.fields['f_pack'].initial = True