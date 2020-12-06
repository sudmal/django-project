from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import models
from django.db.models import Func
from urllib.parse import unquote
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import cache_page
import django_tables2 as tables
from django_tables2.export.export import TableExport
from django_tables2.export.views import ExportMixin
from .models import Exchange,Youscore,ReestrStaging,CreditStaging,NlCredit,NlOrg,NlProduct,NlReestr
from django.db.models import Count, Sum, Q, Avg, Subquery, OuterRef, F, FloatField, Max
from .forms import SearchFormOrg,DatesStartEndForm
import datetime
import requests
import json 

from django.contrib.postgres.aggregates import ArrayAgg
from django_tables2 import RequestConfig
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth


# if now is not jan or feb, year is current year, other way - previus
year = str((datetime.date.today() - datetime.timedelta(days=59)).year)

def logUserData(request):
    print(request.META['REMOTE_ADDR'])



class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()


def autocomplete_tm(request):
    titles = list()
    return JsonResponse(titles, safe=False)

def sales_autocomplete_org(request):
    titles = list()
    if 'term' in request.GET:
        found_org = NlReestr.objects.filter(Q(seller__name__icontains=request.GET.get('term')) |Q(seller__edrpou__startswith=request.GET.get('term')) )\
            .values('seller__name').annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).distinct().order_by('-sum')
        for tm in found_org:
            titles.append(tm['seller__name'])
    if len(titles)==0:
        titles.append("Ничего не найдено")
    return JsonResponse(titles, safe=False)

def getFirmName(str1):
    st=''
    result=''
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
        for s in st[1:]:
            result=result+s
    else:
        result=str1
    return(result)


def getRecDates():
    dates_dict={}
    return dates_dict

def generateOrder(request,default_sort_order,default_sort_field):
    #symbol for query
    sort_order_symbol=''

    sort_order=default_sort_order
    sort_field=default_sort_field
    # change sort order for link and generate symbol for current query
    if request.GET.get('sort_order'):
        if request.GET.get('sort_order')=='asc':
            sort_order='desc'  # next link status   
        if request.GET.get('sort_order')=='desc':
            sort_order='asc'  # next link status
            sort_order_symbol='-' # current query
    if request.GET.get('sort_field'):
        sort_field=request.GET.get('sort_field')
    order={'sort_order_symbol':sort_order_symbol,'sort_order':sort_order,'sort_field':sort_field}
    return order


@login_required(login_url='login')
def index(request):
    return render(request,'inner/index.html')

@login_required(login_url='login')
def test(request):
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    testq=NlCredit.objects.filter(seller__edrpou=1111111,ordering_date__range=[start_date, end_date]).values('buyer__edrpou','buyer__name').distinct().annotate(month=TruncMonth('ordering_date')).values('month').annotate(c=Count('id')).order_by()
    print(testq.query)
    context={
        'year':year,
        'testq':testq,
    }
    return render(request,'inner/test.html',context)

@login_required(login_url='login')
def SalesIndividual(request):
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    currency = User.objects.get(username=request.user).profile.currency
    DatesForm=DatesStartEndForm()
    if request.GET.get('start_date'):
        DatesForm = DatesStartEndForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        DatesForm.end_date = request.GET.get('end_date')
        end_date=request.GET.get('end_date')
    searchFormOrg=SearchFormOrg()
    organisations=[]

    if request.GET.get('search_string'):
        searchFormOrg = SearchFormOrg(request.GET)
        organisations=NlReestr.objects.filter(Q(seller__name__icontains=request.GET.get('search_string'))|Q(seller__edrpou__icontains=request.GET.get('search_string')))\
            .values('seller__name','seller__edrpou').distinct()
        if currency == 'UAH':
            organisations=organisations.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).distinct().order_by('-sum')
        elif currency == 'EUR':
            organisations=organisations.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/32)).distinct().order_by('-sum')
        elif currency == 'USD':
            organisations=organisations.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/28)).distinct().order_by('-sum')   
         
    context={
        'organisations':organisations,
        'currency':currency,
        'searchFormOrg':searchFormOrg,
        'DatesForm':DatesForm,
        'start_date':start_date,
        'end_date':end_date,
    }
    return render(request,'inner/SalesIndividual.html',context)

@login_required(login_url='login')
def SalesIndividualFirmShow(request,edrpou_num):
    currency = User.objects.get(username=request.user).profile.currency
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    DatesForm=DatesStartEndForm()
    if request.GET.get('start_date'):
        DatesForm = DatesStartEndForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        DatesForm.end_date = request.GET.get('end_date')
        end_date=request.GET.get('end_date')
    seller_name=NlOrg.objects.get(edrpou=edrpou_num).name
    buyers_dict = {}
    buyers=NlReestr.objects.filter(seller__edrpou=edrpou_num,ordering_date__range=[start_date, end_date]).values('buyer__edrpou','buyer__name').distinct()
    if currency == 'UAH':
        buyers=buyers.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).distinct().order_by('-sum')
    elif currency == 'EUR':
        buyers=buyers.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))).distinct().order_by('-sum')
    elif currency == 'USD':
        buyers=buyers.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))).distinct().order_by('-sum')
    #print(buyers.query)
    buyers_list=[]
    for b in buyers:
        cur_firm={}
        cur_firm.update({'buyer__name':b['buyer__name']})
        cur_firm.update({'buyer__edrpou':b['buyer__edrpou']})
        cur_firm.update({'sum':b['sum']})
        """per_mnth_sum= NlReestr.objects.filter(seller__edrpou=edrpou_num,buyer__edrpou=cur_firm['buyer__edrpou'],ordering_date__range=[start_date, end_date]).annotate(m=Month('ordering_date')).values('m')
        if currency == 'UAH':
            per_mnth_sum=per_mnth_sum.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).distinct()
        elif currency == 'EUR':
            per_mnth_sum=per_mnth_sum.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))).distinct()
        elif currency == 'USD':
            per_mnth_sum=per_mnth_sum.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))).distinct()
        mnth_summ_list=[]
        for m in range(12):
            mnth_summ_list.append(0)
        for m in range(12):
            for pms in per_mnth_sum:
                    mnth_summ_list[pms['m']-1]=pms['sum']
        #print (mnth_summ_list)
        cur_firm.update({'per_month_sums':mnth_summ_list})"""
        buyers_list.append(cur_firm)
        #print(buyers_list)
        #Needs for django template generation
        mnth_list=[1,2,3,4,5,6,7,8,9,0,11,12]
    context={
        'buyers_list':buyers_list,
        'edrpou_num':edrpou_num,
        'seller_name':seller_name,
        'currency':currency,
        'DatesForm':DatesForm,
        'start_date':start_date,
        'end_date':end_date,
        'mnth_list':mnth_list,
    }
    return render(request,'inner/SalesIndividualFirmShow.html',context)