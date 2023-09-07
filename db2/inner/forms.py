from django import forms
from .models import NlReestr
from django.db.models import Max
import datetime 
from django.db.models.functions import ExtractYear
from django.forms.fields import BooleanField,IntegerField
from .models import NlReestr,NlOrg,NlOrgClass

reestr_years = NlReestr.objects.extra(select={'year':"extract(year from ordering_date)"}).distinct().values('year').order_by('year')
choices_years=[]
for yr in reestr_years:
    add_yr=str(int(yr['year']))
    choices_years.append((add_yr,add_yr))



class DateInput(forms.DateInput):
    input_type='date'

year = str((datetime.date.today() - datetime.timedelta(days=120)).year)
#print(year)
db_max_date=str(NlReestr.objects.filter(ordering_date__range=[str(year)+'-01-01', str(year)+'-12-31']).aggregate(Max('ordering_date'))['ordering_date__max'])

class SearchFormOrg(forms.Form):
    search_string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'yes','placeholder': 'Введите наименование или ЕДРПОУ','id':'org_search'}), max_length=255)

class RecSearchForm(forms.Form):
    search_string = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'yes','placeholder': 'Введите запрос','id':'db_search'}), max_length=255)
class DatesStartEndForm(forms.Form):
    start_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':year+'-01-01'}))
    end_date = forms.DateField(input_formats='%Y,%m,%d',widget=DateInput(attrs={'class': 'form-control date-inline-select','value':db_max_date}))

class NlYearSelectForm(forms.Form):
    CHOICES = choices_years
    selected_year = forms.ChoiceField(label='', choices=CHOICES,initial=year, widget=forms.Select(attrs={'class':'form-control'}))

#class CompetitorsChoice(forms.Form):
#   cmpt_list = NlReestr.objects.filter(seller__class_field__name='HORECA').values('seller__name','seller__edrpou').distinct()
#   print(cmpt_list)
#   CHOICES=[]
    # {'competitor_code': 43486282, 'competitor_name': None, 'competitor_surname': 'ТОВАРИСТВО З ОБМЕЖЕНОЮ ВIДПОВIДАЛЬНIСТЮ "САМОРОДОК ТМ"'}
#    for c in cmpt_list:
#        CHOICES.append((str(c['seller__edrpou']),str(c['seller__edrpou'])+' - '+str(c['seller__name'])))
    #print(CHOICES)
#    cmpt_selector = forms.ChoiceField(label='', choices=CHOICES, widget=forms.Select(attrs={'class':'form-control'}))


class FirmTypeSelectForm(forms.Form):
    f_horeca = BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input','id':'f_horeca'}))
    f_eat = BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input ','id':'f_eat'}))
    f_pack = BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input ','id':'f_pack'}))
    f_other = BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input ','id':'f_other'}))
    min_sum = IntegerField(required=False,max_value=999999999999,min_value=0,widget=forms.NumberInput(attrs={'class':'form-control-input','id':'max_summ'}))
    def __init__(self, *args, **kwargs):
        super(FirmTypeSelectForm, self).__init__(*args, **kwargs)
        self.fields['f_horeca'].initial = True
        self.fields['f_eat'].initial = True
        self.fields['f_pack'].initial = True