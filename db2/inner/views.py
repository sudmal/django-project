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
from .forms import SearchFormOrg,DatesStartEndForm,NlYearSelectForm
import pandas as pd
import datetime
import requests
import json 

from django.contrib.postgres.aggregates import ArrayAgg
from django_tables2 import RequestConfig
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth


# if now is not jan or feb, year is current year, other way - previus
def getCurrentYear():
    return str((datetime.date.today() - datetime.timedelta(days=59)).year)

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
    year=getCurrentYear()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
            ### FIX THIS!  # Получаем все записи из базы, соответствующие buyer_id и передаем в словарь {buyer_id,date,cost}
                           # считаем сумму для каждого месяца
                           # for m in 1...12
    print('Get data from db')
    df=pd.DataFrame(list(NlReestr.objects.filter(seller__edrpou=41189553,ordering_date__range=[start_date, end_date]).values('buyer__edrpou','ordering_date','one_product_cost','count','exchange__eur_com','exchange__eur_nbu','exchange__usd_com','exchange__usd_nbu','exchange__eur_mb_buy','exchange__eur_mb_sale')))
    '''print('Generate df_data list')
    df_data=[]
    for t in ttt1:
        df_data.append(t)
    print('done')
    df=pd.DataFrame(df_data)'''
    df['ordering_date'] = pd.to_datetime(df['ordering_date'])
    print(df.head())
    print(df.dtypes)
    edrpous=df['buyer__edrpou'].unique()
    print (edrpous)
    for e in edrpous:    
        df1=df[df['buyer__edrpou']==e].groupby(df['ordering_date'].dt.strftime('%m'))['one_product_cost'].sum()

    context={
        'year':year,
    }
    return render(request,'inner/test.html',context)

@login_required(login_url='login')
def SalesIndividual(request):
    YearSelectForm=NlYearSelectForm()
    currency = User.objects.get(username=request.user).profile.currency
    year=getCurrentYear()
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')
    searchFormOrg=SearchFormOrg()
    organisations=[]
    if request.GET.get('search_string'):
        searchFormOrg = SearchFormOrg(request.GET)
        organisations=NlReestr.objects.filter(Q(ordering_date__year=year)&(Q(seller__name__icontains=request.GET.get('search_string'))|Q(seller__edrpou__icontains=request.GET.get('search_string'))))\
            .values('seller__name','seller__edrpou').distinct()
        if currency == 'UAH':
            organisations=organisations.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).order_by('-sum')
        elif currency == 'EUR':
            organisations=organisations.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))).order_by('-sum')
        elif currency == 'USD':
            organisations=organisations.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))).order_by('-sum')   
    context={
        'organisations':organisations,
        'currency':currency,
        'searchFormOrg':searchFormOrg,
        'YearSelectForm':YearSelectForm,
        'year':year
    }
    return render(request,'inner/SalesIndividual.html',context)

@login_required(login_url='login')
def SalesIndividualFirmShow(request,edrpou_num):
    year=getCurrentYear()
    YearSelectForm=NlYearSelectForm()
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')

    currency = User.objects.get(username=request.user).profile.currency
    seller_name=NlOrg.objects.get(edrpou=edrpou_num).name
    buyers_dict = {}
    buyers=NlReestr.objects.filter(seller__edrpou=edrpou_num,ordering_date__year=year).values('buyer_id','buyer__edrpou','buyer__name').distinct()
    if currency == 'UAH':
        buyers=buyers.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).order_by('-sum')
    elif currency == 'EUR':
        buyers=buyers.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))).order_by('-sum')
    elif currency == 'USD':
        buyers=buyers.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))).order_by('-sum')
    #print(buyers.query)
    buyers_list=[]
    totals=[]
    for m in range(1,13):
        t_sum=NlReestr.objects.filter(seller__edrpou=edrpou_num,ordering_date__year=year,ordering_date__month=m)
        if currency == 'UAH':
            t_sum=t_sum.aggregate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))
        elif currency == 'EUR':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))
        elif currency == 'USD':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))
        totals.append(t_sum['sum'])
    t_sum=NlReestr.objects.filter(seller__edrpou=edrpou_num,ordering_date__year=year)
    if currency == 'UAH':
        t_sum=t_sum.aggregate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))
    elif currency == 'EUR':
        t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))
    elif currency == 'USD':
        t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))
    totals.append(t_sum['sum'])
    for b in buyers:
        cur_firm={}
        cur_firm.update({'buyer_id':b['buyer_id']})
        cur_firm.update({'buyer__name':b['buyer__name']})
        cur_firm.update({'buyer__edrpou':b['buyer__edrpou']})
        cur_firm.update({'sum':b['sum']})
        #print (cur_firm['buyer__edrpou'])
        b_pms=NlReestr.objects.filter(seller__edrpou=edrpou_num,buyer_id=cur_firm['buyer_id'],ordering_date__year=year).annotate(month=TruncMonth('ordering_date')).values('month') 
        if currency == 'UAH':
            b_pms=b_pms.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).order_by()
        elif currency == 'EUR':
            b_pms=b_pms.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))).order_by()
        elif currency == 'USD':
            b_pms=b_pms.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))).order_by()
        pms=[] # per_monnth_summs
        for m in range(1,13):
            pms.append(float(0.0))
        for bb in b_pms:
            bb['month'] = int(str(bb['month'])[5:7])
            pms[bb['month']-1]=bb['sum']
        cur_firm.update({'pms':pms})
        #print(cur_firm)

        buyers_list.append(cur_firm)


    paginator = Paginator(buyers_list, 10)
    page_number = request.GET.get('page')
    try:
        buyers_list = paginator.page(page_number)
    except PageNotAnInteger:
        buyers_list = paginator.page(1)
    except EmptyPage:
        buyers_list = paginator.page(paginator.num_pages) 

    
    #Needs for django template generation
    mnth_list=["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]

    context={
        'buyers_list':buyers_list,
        'totals':totals,
        'edrpou_num':edrpou_num,
        'seller_name':seller_name,
        'currency':currency,
        'mnth_list':mnth_list,
        'year':year,
        'YearSelectForm':YearSelectForm,
    }
    return render(request,'inner/SalesIndividualFirmShow.html',context)

@login_required(login_url='login')
def SalesIndividualFirmRaw(request,edrpou_num,buyer_code):
    year=getCurrentYear()
    currency = User.objects.get(username=request.user).profile.currency
    if request.GET.get('selected_year'):
        year=request.GET.get('selected_year')
        print(year)
    raw_records= NlReestr.objects.filter(seller__edrpou=edrpou_num,buyer__edrpou=buyer_code,ordering_date__year=year).values('product__name','product__product_code','unit','count','ordering_date')
    if currency == 'UAH':
        raw_records=raw_records.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).annotate(one_product_cost=Sum(F('one_product_cost')+F('one_product_cost')*0.2)).order_by('ordering_date')
    elif currency == 'EUR':
        raw_records=raw_records.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))).annotate(one_product_cost=Sum((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__eur_mb_sale'))).order_by('ordering_date')
    elif currency == 'USD':
        raw_records=raw_records.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))).annotate(one_product_cost=Sum((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__usd_com'))).order_by('ordering_date')
    print(raw_records.query)
    paginator = Paginator(raw_records, 25)
    page_number = request.GET.get('page')
    try:
        raw_records = paginator.page(page_number)
    except PageNotAnInteger:
        raw_records = paginator.page(1)
    except EmptyPage:
        raw_records = paginator.page(paginator.num_pages)
    context={
        'currency':currency,
        'edrpou_num':edrpou_num,
        'buyer_code':buyer_code,
        'raw_records':raw_records,
        'year':year,
    }
    return render(request,'inner/SalesIndividualFirmRaw.html',context)