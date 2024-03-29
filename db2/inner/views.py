from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.db import models
from django.db.models import Func,IntegerField
from urllib.parse import unquote
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import cache_page
import django_tables2 as tables
from django_tables2.export.export import TableExport
from django_tables2.export.views import ExportMixin
from .models import Exchange,Youscore,ReestrStaging,CreditStaging,NlCredit,NlOrg,NlOrgClass,NlProduct,NlReestr,NlFilter,Competitors,Organisation,NlPeriodPurchases,NlPeriodSales
from django.db.models import Count, Sum, Q, Avg, Subquery, OuterRef, F, FloatField, Max
from django.db.models import FloatField
from django.db.models.functions import Cast
from .forms import SearchFormOrg,DatesStartEndForm,NlYearSelectForm,FirmTypeSelectForm,RecSearchForm
from .tables import RecordsSearchTable,Top100Table
import pandas as pd
import psycopg2 as pg
import datetime
import requests
import json 

from django.contrib.postgres.aggregates import ArrayAgg
from django_tables2 import RequestConfig
from django.contrib.auth.models import User
from django.db.models.functions import TruncMonth

print(pd.__version__)

year = str((datetime.date.today() - datetime.timedelta(days=120)).year)
db_max_date=str(NlReestr.objects.filter(ordering_date__range=[str(year)+'-01-01', str(year)+'-12-31']).aggregate(Max('ordering_date'))['ordering_date__max'])

def getCurrentRowsPerPage(request):
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=99999999999
    return num_per_page
    
# if now is not jan or feb, year is current year, other way - previus
def getCurrentYear():
    return str((datetime.date.today() - datetime.timedelta(days=120)).year)
class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH from %(expressions)s)'
    output_field = models.IntegerField()
class Round(Func):
    function = 'ROUND'
    template='%(function)s(%(expressions)s::numeric, 0)'



class Round2(Func):
    function = "ROUND"
    template = "%(function)s(%(expressions)s::numeric, 2)"

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

def clients_autocomplete_org(request):
    titles = list()
    if 'term' in request.GET:
        found_org = NlReestr.objects.filter(Q(buyer__name__icontains=request.GET.get('term')) |Q(buyer__edrpou__startswith=request.GET.get('term')) )\
            .values('buyer__name').annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).distinct().order_by('-sum')
        for tm in found_org:
            titles.append(tm['buyer__name'])
    if len(titles)==0:
        titles.append("Ничего не найдено")
    return JsonResponse(titles, safe=False)

def purchases_autocomplete_org(request):
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



def Youscore_get(competitors_top):
    year=2019
    api_key='1f0900000ebe229bcca6e39128b59d5be1fa2bb7'
    fin_data={}
    ved_data={}
    for c_top in competitors_top:
        edrpou=c_top['seller__edrpou']
        ysr="https://api.youscore.com.ua/v1/financialIndicators/"+str(edrpou)+"/years/"+str(int(year)-1)+"?apiKey="+api_key
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}
        ret_fin=''
        ret_ved=''
        if Youscore.objects.filter(request=ysr):
            db_reply=Youscore.objects.filter(request=ysr).values('jsonreply')
            ret_fin=str(db_reply[0]['jsonreply'])

        else:
            result = requests.get(ysr, headers=headers)
            save_result=Youscore.objects.create(request=ysr,jsonreply=result.text)
            ret_fin=str(result.text)

        #https://api.youscore.com.ua/v1/externalEconomies/38797324?apiKey=1f0900000ebe229bcca6e39128b59d5be1fa2bb7
        #https://api.youscore.com.ua/v1/externalEconomies/38797324?year=2020&apiKey=1f0900000ebe229bcca6e39128b59d5be1fa2bb7
                
        ysr="https://api.youscore.com.ua/v1/externalEconomies/"+str(edrpou)+"?year="+str(int(year)-1)+"&apiKey="+api_key
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}
        
        if Youscore.objects.filter(request=ysr):
            db_reply=Youscore.objects.filter(request=ysr).values('jsonreply')
            ret_ved=str(db_reply[0]['jsonreply'])
        else:

            result = requests.get(ysr, headers=headers)
            if result:
                save_result=Youscore.objects.create(request=ysr,jsonreply=result.text)
                ret_ved=str(result.text)

        fin_data.update({edrpou:json.loads(ret_fin)})
        ved_data.update({edrpou:json.loads(ret_ved)})
    ret_dict={
        'fin':fin_data,
        'ved':ved_data,
    }
    return ret_dict


@login_required(login_url='login')
def index(request):
    return render(request,'inner/index.html')

@login_required(login_url='login')
def test(request):
    # https://daruse.ru/prostaya-filtracziya-tabliczyi-na-jquery
    year=getCurrentYear()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    competitors=NlReestr.objects.all().values('seller__edrpou','seller__name','seller__class_field__name')\
            .annotate(total_cost=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2),\
                total_count=Count('one_product_cost')).order_by('-total_cost')

    edrpou_list=[]
    context={
        'competitors':competitors,
        'year':year,
        }
    context.update({'help_page_id':1})
    return render(request,'inner/test.html',context)

@login_required(login_url='login')
def SalesIndividual(request):
    YearSelectForm=NlYearSelectForm()
    currency = User.objects.get(username=request.user).profile.currency
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=99999999999

    year=getCurrentYear()
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')
    #print(year)
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
        #print(organisations.query)
    context={
        'organisations':organisations,
        'currency':currency,
        'searchFormOrg':searchFormOrg,
        'YearSelectForm':YearSelectForm,
        'year':year
    }

    context.update({'help_page_id':11})
    return render(request,'inner/SalesIndividual.html',context)

@login_required(login_url='login')
def SalesIndividualFirmShow(request,edrpou_num):
    year=getCurrentYear()
    YearSelectForm=NlYearSelectForm()
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=99999999999
    currency = User.objects.get(username=request.user).profile.currency
    seller_name=NlOrg.objects.get(edrpou=edrpou_num).name
    buyers_dict = {}
    buyers=NlReestr.objects.filter(seller__edrpou=edrpou_num,ordering_date__year=year).values('buyer_id','buyer__edrpou','buyer__name').distinct()
    if currency == 'UAH':
        buyers=buyers.annotate(sum=Round2(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by('-sum')
    elif currency == 'EUR':
        buyers=buyers.annotate(sum=Round2(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by('-sum')
    elif currency == 'USD':
        buyers=buyers.annotate(sum=Round2(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by('-sum')
    buyers=buyers.filter(sum__isnull=False)
    buyers_list=[]
    period_dates={}
    for m in range(1,13):
        check_period=str(year)+'-'+str(m).zfill(2)
        if NlPeriodSales.objects.filter(edrpou=edrpou_num).extra(where=["(to_char(min_date, 'YYYY-MM') <= '"+check_period+"' and to_char(max_date, 'YYYY-MM') >= '"+check_period+"')"]).count() >0:
            period_dates_query=NlPeriodSales.objects.filter(edrpou=edrpou_num).extra(where=["(to_char(min_date, 'YYYY-MM') <= '"+check_period+"' and to_char(max_date, 'YYYY-MM') >= '"+check_period+"')"]).values('min_date','max_date','import_date')
            
            period_dates.update({m:period_dates_query[0]['min_date'].strftime('%d.%m.%Y') +' - '+ period_dates_query[0]['max_date'].strftime('%d.%m.%Y') + ' (import date: ' + period_dates_query[0]['import_date'].strftime('%d.%m.%Y')+ ')'})
        else:
            period_dates.update({m:False})
    #print(period_dates)
    totals=[]
    # Total sums
    '''for m in range(1,13):
        t_sum=NlReestr.objects.filter(seller__edrpou=edrpou_num,ordering_date__year=year,ordering_date__month=m)
        if currency == 'UAH':
            t_sum=t_sum.aggregate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))
        elif currency == 'EUR':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))
        elif currency == 'USD':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))
        totals.append(t_sum['sum'])'''
    t_sum=NlReestr.objects.filter(seller__edrpou=edrpou_num,ordering_date__year=year)
    if currency == 'UAH':
        t_sum=t_sum.aggregate(sum=Round2(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)))
    elif currency == 'EUR':
        t_sum=t_sum.aggregate(sum=Round2(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))))
    elif currency == 'USD':
        t_sum=t_sum.aggregate(sum=Round2(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))))
    total_year=t_sum['sum']
    for b in buyers:
        cur_firm={}
        cur_firm.update({'buyer_id':b['buyer_id']})
        cur_firm.update({'buyer__name':b['buyer__name']})
        cur_firm.update({'buyer__edrpou':b['buyer__edrpou']})
        cur_firm.update({'sum':b['sum']})
        #print (cur_firm['buyer__edrpou'])
        # buyers per month summs
        b_pms=NlReestr.objects.filter(seller__edrpou=edrpou_num,buyer_id=cur_firm['buyer_id'],ordering_date__year=year).annotate(month=TruncMonth('ordering_date')).values('month') 
        if currency == 'UAH':
            b_pms=b_pms.annotate(sum=Round2(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by()
        elif currency == 'EUR':
            b_pms=b_pms.annotate(sum=Round2(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by()
        elif currency == 'USD':
            b_pms=b_pms.annotate(sum=Round2(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by()
        pms=[] # per_monnth_summs
        for m in range(1,13):
            pms.append(float(0.0))
        for bb in b_pms:
            bb['month'] = int(str(bb['month'])[5:7])
            pms[bb['month']-1]=bb['sum']
        cur_firm.update({'pms':pms})
        #print(cur_firm)

        buyers_list.append(cur_firm)


    paginator = Paginator(buyers_list, getCurrentRowsPerPage(request))
    page_number = request.GET.get('page')
    try:
        buyers_list = paginator.page(page_number)
    except PageNotAnInteger:
        buyers_list = paginator.page(1)
    except EmptyPage:
        buyers_list = paginator.page(paginator.num_pages) 

    print(period_dates)
    #Needs for django template generation
    mnth_list=["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
    context={
        'buyers_list':buyers_list,
        'total_year':total_year,
        'edrpou_num':edrpou_num,
        'seller_name':seller_name,
        'currency':currency,
        'mnth_list':mnth_list,
        'year':year,
        'YearSelectForm':YearSelectForm,
        'period_dates':period_dates,
    }
    context.update({'help_page_id':11})
    return render(request,'inner/SalesIndividualFirmShow.html',context)

@login_required(login_url='login')
def SalesIndividualFirmRaw(request,edrpou_num,buyer_code):
    year=getCurrentYear()
    currency = User.objects.get(username=request.user).profile.currency
    if request.GET.get('selected_year'):
        year=request.GET.get('selected_year')
    raw_records= NlReestr.objects.filter(seller__edrpou=edrpou_num,buyer__edrpou=buyer_code,ordering_date__year=year).values('product__name','product__product_code','unit','count','ordering_date')
    if currency == 'UAH':
        raw_records=raw_records.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).annotate(one_product_cost=Sum(F('one_product_cost')+F('one_product_cost')*0.2)).order_by('ordering_date')
    elif currency == 'EUR':
        raw_records=raw_records.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))).annotate(one_product_cost=Sum((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__eur_mb_sale'))).order_by('ordering_date')
    elif currency == 'USD':
        raw_records=raw_records.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))).annotate(one_product_cost=Sum((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__usd_com'))).order_by('ordering_date')

    if request.GET.get('month'):
        raw_records = raw_records.filter(ordering_date__year=year,ordering_date__month=request.GET.get('month'))
    
#    # Если в GET запросе присутствует параметр _export возвращаем не данные для шаблона, а xlsx-таблицу
#    export_format = request.GET.get("_export", None)
#    if TableExport.is_valid_format(export_format):
#        exporter = TableExport(export_format, raw_records, dataset_kwargs={"title": edrpou_num})
#        return exporter.response(filename="Nalog_Export_{0}_{1}.{2}".format(edrpou_num,year,export_format))
    
    paginator = Paginator(raw_records, getCurrentRowsPerPage(request))
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
    context.update({'help_page_id':11})
    return render(request,'inner/SalesIndividualFirmRaw.html',context)

@login_required(login_url='login')
def SalesCompetitorsComparse(request):
    year=getCurrentYear()
    currency = User.objects.get(username=request.user).profile.currency
    YearSelectForm=NlYearSelectForm()
    firmTypeSelectForm = FirmTypeSelectForm()
    if request.GET.get('firm_filter_set'):
        firmTypeSelectForm = FirmTypeSelectForm(request.GET)
    filter_dict={
        'f_horeca':False,
        'f_eat':False,
        'f_pack':False,
        'f_other':False,
    }
    if firmTypeSelectForm['f_horeca'].value():
        filter_dict.update({'f_horeca':True})
    if firmTypeSelectForm['f_eat'].value():
        filter_dict.update({'f_eat':True})
    if firmTypeSelectForm['f_pack'].value():
        filter_dict.update({'f_pack':True})
    if firmTypeSelectForm['f_other'].value():
        filter_dict.update({'f_other':True})
        
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')
    competitors= Competitors.objects.all().values_list('competitor_code', flat=True)
    #print(competitors.query)
    f_eat=NlFilter.objects.filter(type="eat").values_list('edrpou', flat=True)
    f_pack=NlFilter.objects.filter(type="pack").values_list('edrpou', flat=True)
    f_other=NlFilter.objects.filter(type="other").values_list('edrpou', flat=True)
    f_horeca=Competitors.objects.exclude(Q(competitor_code__in=f_eat) | Q(competitor_code__in=f_pack) | Q(competitor_code__in=f_other)).values_list('competitor_code', flat=True)

    organisations = NlReestr.objects.filter(ordering_date__year=year)
    if not filter_dict['f_horeca']:
        f_horeca = ['111111']
    if not filter_dict['f_eat']:
        f_eat = ['111111']
    if not filter_dict['f_pack']:
        f_pack = ['111111']
    if not filter_dict['f_other']:
        f_other = ['111111']
    organisations=organisations.filter(Q(seller__edrpou__in=f_horeca) | Q(seller__edrpou__in=f_eat) | Q(seller__edrpou__in=f_pack) |Q(seller__edrpou__in=f_other) )

    organisations = organisations.values('seller_id','seller__name','seller__edrpou').distinct()
    #print (organisations.query)
    if currency == 'UAH':
            organisations=organisations.annotate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by('-sum')
    elif currency == 'EUR':
            organisations=organisations.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by('-sum')
    elif currency == 'USD':
            organisations=organisations.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by('-sum')
    organisations=organisations.filter(sum__isnull=False)

    organisations_list=[]
    totals=[]
    # Total sums
    for m in range(1,13):
        t_sum=NlReestr.objects.filter(Q(seller__edrpou__in=f_horeca) | Q(seller__edrpou__in=f_eat) | Q(seller__edrpou__in=f_pack) |Q(seller__edrpou__in=f_other) ).filter(ordering_date__year=year,ordering_date__month=m)
        if currency == 'UAH':
            t_sum=t_sum.aggregate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))
        elif currency == 'EUR':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))
        elif currency == 'USD':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))
        totals.append(t_sum['sum'])
    importers=[]
    for o in organisations:
        try:
            imp=Organisation.objects.get(edrpou=o['seller__edrpou'])
        except Organisation.DoesNotExist:
            imp = False
        cur_firm={}
        if imp:
            cur_firm.update({'is_importer':True})
        else:
            cur_firm.update({'is_importer':False})
        
        cur_firm.update({'seller_id':o['seller_id']})
        cur_firm.update({'seller__name':o['seller__name']})
        cur_firm.update({'seller__edrpou':o['seller__edrpou']})
        cur_firm.update({'sum':o['sum']})
        #print (cur_firm['seller__edrpou'])
        o_pms=NlReestr.objects.filter(ordering_date__year=year).filter(seller_id=cur_firm['seller_id']).filter(Q(seller__edrpou__in=f_horeca) | Q(seller__edrpou__in=f_eat) | Q(seller__edrpou__in=f_pack) |Q(seller__edrpou__in=f_other) ).annotate(month=TruncMonth('ordering_date')).values('month') 
        if currency == 'UAH':
            o_pms=o_pms.annotate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by()
        elif currency == 'EUR':
            o_pms=o_pms.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by()
        elif currency == 'USD':
            o_pms=o_pms.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by()
        pms=[] # per_monnth_summs
        for m in range(1,13):
            pms.append(float(0.0))
        for oo in o_pms:
            oo['month'] = int(str(oo['month'])[5:7])
            pms[oo['month']-1]=oo['sum']
        cur_firm.update({'pms':pms})
        #print(cur_firm)

        organisations_list.append(cur_firm)


    paginator = Paginator(organisations_list, getCurrentRowsPerPage(request))
    page_number = request.GET.get('page')
    try:
        organisations_list = paginator.page(page_number)
    except PageNotAnInteger:
        organisations_list = paginator.page(1)
    except EmptyPage:
        organisations_list = paginator.page(paginator.num_pages)
    mnth_list=["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
    context={
        'mnth_list':mnth_list,
        'competitors':competitors,
        'organisations':organisations_list,
        'totals':totals,
        'currency':currency,
        'year':year,
        'YearSelectForm':YearSelectForm,
        'firmTypeSelectForm':firmTypeSelectForm,
    }
    context.update({'help_page_id':12})
    return render(request,'inner/SalesCompetitorsComparse.html',context)

@login_required(login_url='login')
def ClientsCompetitorsIndividualSearch(request):
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
        organisations=NlReestr.objects.filter(Q(ordering_date__year=year)&(Q(buyer__name__icontains=request.GET.get('search_string'))|Q(buyer__edrpou__icontains=request.GET.get('search_string'))))\
            .values('buyer__name','buyer__edrpou').distinct()
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
    context.update({'help_page_id':14})
    return render(request,'inner/ClientsCompetitorsIndividualSearch.html',context)

@login_required(login_url='login')
def ClientsCompetitorsIndividualShow(request,edrpou_num):
    year=getCurrentYear()
    YearSelectForm=NlYearSelectForm()
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')

    currency = User.objects.get(username=request.user).profile.currency
    buyer_name=NlOrg.objects.get(edrpou=edrpou_num).name
    sellers_dict = {}
    sellers=NlReestr.objects.filter(buyer__edrpou=edrpou_num,ordering_date__year=year).values('seller_id','seller__edrpou','seller__name').distinct()
    if currency == 'UAH':
        sellers=sellers.annotate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by('-sum')
    elif currency == 'EUR':
        sellers=sellers.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by('-sum')
    elif currency == 'USD':
        sellers=sellers.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by('-sum')
    sellers=sellers.filter(sum__isnull=False)
    sellers_list=[]
    totals=[]
    # Total sums
    for m in range(1,13):
        t_sum=NlReestr.objects.filter(buyer__edrpou=edrpou_num,ordering_date__year=year,ordering_date__month=m)
        if currency == 'UAH':
            t_sum=t_sum.aggregate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))
        elif currency == 'EUR':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))
        elif currency == 'USD':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))
        totals.append(t_sum['sum'])
    t_sum=NlReestr.objects.filter(buyer__edrpou=edrpou_num,ordering_date__year=year)
    if currency == 'UAH':
        t_sum=t_sum.aggregate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)))
    elif currency == 'EUR':
        t_sum=t_sum.aggregate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))))
    elif currency == 'USD':
        t_sum=t_sum.aggregate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))))
    totals.append(t_sum['sum'])
    for b in sellers:
        cur_firm={}
        cur_firm.update({'seller_id':b['seller_id']})
        cur_firm.update({'seller__name':b['seller__name']})
        cur_firm.update({'seller__edrpou':b['seller__edrpou']})
        cur_firm.update({'sum':b['sum']})
        #print (cur_firm['seller__edrpou'])
        b_pms=NlReestr.objects.filter(buyer__edrpou=edrpou_num,seller_id=cur_firm['seller_id'],ordering_date__year=year).annotate(month=TruncMonth('ordering_date')).values('month') 
        if currency == 'UAH':
            b_pms=b_pms.annotate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by()
        elif currency == 'EUR':
            b_pms=b_pms.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by()
        elif currency == 'USD':
            b_pms=b_pms.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by()
        pms=[] # per_monnth_summs
        for m in range(1,13):
            pms.append(float(0.0))
        for bb in b_pms:
            bb['month'] = int(str(bb['month'])[5:7])
            pms[bb['month']-1]=bb['sum']
        cur_firm.update({'pms':pms})
        sellers_list.append(cur_firm)


    paginator = Paginator(sellers_list, getCurrentRowsPerPage(request))
    page_number = request.GET.get('page')
    try:
        sellers_list = paginator.page(page_number)
    except PageNotAnInteger:
        sellers_list = paginator.page(1)
    except EmptyPage:
        sellers_list = paginator.page(paginator.num_pages) 

    
    #Needs for django template generation
    mnth_list=["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]

    context={
        'sellers_list':sellers_list,
        'totals':totals,
        'edrpou_num':edrpou_num,
        'buyer_name':buyer_name,
        'currency':currency,
        'mnth_list':mnth_list,
        'year':year,
        'YearSelectForm':YearSelectForm,
    }
    context.update({'help_page_id':14})
    return render(request,'inner/ClientsCompetitorsIndividualShow.html',context)

@login_required(login_url='login')
def ClientsCompetitorsIndividualRaw(request,edrpou_num,seller_code):
    year=getCurrentYear()
    currency = User.objects.get(username=request.user).profile.currency
    if request.GET.get('selected_year'):
        year=request.GET.get('selected_year')
    raw_records= NlReestr.objects.filter(buyer__edrpou=edrpou_num,seller__edrpou=seller_code,ordering_date__year=year).values('product__name','product__product_code','unit','count','ordering_date')
    if currency == 'UAH':
        raw_records=raw_records.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).annotate(one_product_cost=Sum(F('one_product_cost')+F('one_product_cost')*0.2)).order_by('ordering_date')
    elif currency == 'EUR':
        raw_records=raw_records.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))).annotate(one_product_cost=Sum((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__eur_mb_sale'))).order_by('ordering_date')
    elif currency == 'USD':
        raw_records=raw_records.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))).annotate(one_product_cost=Sum((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__usd_com'))).order_by('ordering_date')

    if request.GET.get('month'):
        raw_records = raw_records.filter(ordering_date__year=year,ordering_date__month=request.GET.get('month'))

    paginator = Paginator(raw_records, getCurrentRowsPerPage(request))
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
        'seller_code':seller_code,
        'raw_records':raw_records,
        'year':year,
    }
    context.update({'help_page_id':14})
    return render(request,'inner/ClientsCompetitorsIndividualRaw.html',context)

@login_required(login_url='login')
def ClientsCompetitorsComparse(request):
    year=getCurrentYear()
    currency = User.objects.get(username=request.user).profile.currency
    YearSelectForm=NlYearSelectForm()
    min_sum=1600000
    if currency == 'EUR':
        min_sum=50000
    if currency == 'USD':
        min_sum=60000
    if request.GET.get('min_sum'):
        min_sum=int(request.GET.get('min_sum'))
    firmTypeSelectForm = FirmTypeSelectForm(initial={'min_sum':min_sum})
        
    if request.GET.get('firm_filter_set'):
        firmTypeSelectForm = FirmTypeSelectForm(request.GET)
        min_sum=request.GET.get('min_sum')
    filter_dict={
        'f_horeca':False,
        'f_eat':False,
        'f_pack':False,
        'f_other':False,
    }
    if firmTypeSelectForm['f_horeca'].value():
        filter_dict.update({'f_horeca':True})
    if firmTypeSelectForm['f_eat'].value():
        filter_dict.update({'f_eat':True})
    if firmTypeSelectForm['f_pack'].value():
        filter_dict.update({'f_pack':True})
    if firmTypeSelectForm['f_other'].value():
        filter_dict.update({'f_other':True})
        
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')
    # Список всех конкурентов
    competitors= Competitors.objects.all().values_list('competitor_code', flat=True)
    #print(competitors.query)
    # организации по продуктам питания
    f_eat=NlFilter.objects.filter(type="eat").values_list('edrpou', flat=True)
    # организации по упаковке
    f_pack=NlFilter.objects.filter(type="pack").values_list('edrpou', flat=True)
    # организации - другие
    f_other=NlFilter.objects.filter(type="other").values_list('edrpou', flat=True)

    # HORECA - организации - все, кто не попадает под предыдущие три
    f_horeca=Competitors.objects.exclude(Q(competitor_code__in=f_eat) | Q(competitor_code__in=f_pack) | Q(competitor_code__in=f_other)).values_list('competitor_code', flat=True)
    
    organisations = NlReestr.objects.filter(ordering_date__year=year)
    #print (organisations.query)
    if not filter_dict['f_horeca']:
        f_horeca = ['111111']
    if not filter_dict['f_eat']:
        f_eat = ['111111']
    if not filter_dict['f_pack']:
        f_pack = ['111111']
    if not filter_dict['f_other']:
        f_other = ['111111']
    organisations=organisations.filter(Q(seller__edrpou__in=f_horeca) | Q(seller__edrpou__in=f_eat) | Q(seller__edrpou__in=f_pack) |Q(seller__edrpou__in=f_other) )
    organisations = organisations.values('buyer_id','buyer__name','buyer__edrpou').distinct()
    
    if currency == 'UAH':
            organisations=organisations.annotate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by('-sum')
    elif currency == 'EUR':
            organisations=organisations.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by('-sum')
    elif currency == 'USD':
            organisations=organisations.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by('-sum')
    organisations=organisations.filter(Q(sum__gte=min_sum))
    print (organisations.query)
    organisations_list=[]
    totals=[]
    # Total sums
    for m in range(1,13):
        t_sum=NlReestr.objects.filter(Q(seller__edrpou__in=f_horeca) | Q(seller__edrpou__in=f_eat) | Q(seller__edrpou__in=f_pack) |Q(seller__edrpou__in=f_other) ).filter(ordering_date__year=year,ordering_date__month=m)
        if currency == 'UAH':
            t_sum=t_sum.aggregate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))
        elif currency == 'EUR':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))
        elif currency == 'USD':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))
        totals.append(t_sum['sum'])

    #print (totals)
    importers=[]
    for o in organisations:
        #print(o['buyer__edrpou'])
        try:
            imp=Organisation.objects.get(edrpou=o['buyer__edrpou'])
        except Organisation.DoesNotExist:
            imp = False
        cur_firm={}
        if imp:
            cur_firm.update({'is_importer':True})
        else:
            cur_firm.update({'is_importer':False})
        
        cur_firm.update({'buyer_id':o['buyer_id']})
        cur_firm.update({'buyer__name':o['buyer__name']})
        cur_firm.update({'buyer__edrpou':o['buyer__edrpou']})
        cur_firm.update({'sum':o['sum']})
        #print (cur_firm['buyer__edrpou'])
        o_pms=NlReestr.objects.filter(ordering_date__year=year).filter(buyer_id=cur_firm['buyer_id']).filter(Q(seller__edrpou__in=f_horeca) | Q(seller__edrpou__in=f_eat) | Q(seller__edrpou__in=f_pack) |Q(seller__edrpou__in=f_other) ).annotate(month=TruncMonth('ordering_date')).values('month') 
        if currency == 'UAH':
            o_pms=o_pms.annotate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by()
        elif currency == 'EUR':
            o_pms=o_pms.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by()
        elif currency == 'USD':
            o_pms=o_pms.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by()
        pms=[] # per_monnth_summs
        for m in range(1,13):
            pms.append(float(0.0))
        for oo in o_pms:
            oo['month'] = int(str(oo['month'])[5:7])
            pms[oo['month']-1]=oo['sum']
        cur_firm.update({'pms':pms})
        #print(cur_firm)

        organisations_list.append(cur_firm)


    paginator = Paginator(organisations_list, getCurrentRowsPerPage(request))
    page_number = request.GET.get('page')
    try:
        organisations_list = paginator.page(page_number)
    except PageNotAnInteger:
        organisations_list = paginator.page(1)
    except EmptyPage:
        organisations_list = paginator.page(paginator.num_pages)
    mnth_list=["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]
    print(year)
    context={
        'min_sum':min_sum,
        'mnth_list':mnth_list,
        'competitors':competitors,
        'organisations':organisations_list,
        'totals':totals,
        'currency':currency,
        'year':year,
        'YearSelectForm':YearSelectForm,
        'firmTypeSelectForm':firmTypeSelectForm,
    }
    context.update({'help_page_id':15})
    return render(request,'inner/ClientsCompetitorsComparse.html',context)

@login_required(login_url='login')
def PurchasesIndividualSearch(request):
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
        organisations=NlCredit.objects.filter(Q(ordering_date__year=year)&(Q(buyer__name__icontains=request.GET.get('search_string'))|Q(buyer__edrpou__icontains=request.GET.get('search_string'))))\
            .values('buyer__name','buyer__edrpou').distinct()
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
    context.update({'help_page_id':16})
    return render(request,'inner/PurchasesIndividualSearch.html',context)

@login_required(login_url='login')
def PurchasesIndividualFirmShow(request,edrpou_num):
    year=getCurrentYear()
    YearSelectForm=NlYearSelectForm()
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')

    currency = User.objects.get(username=request.user).profile.currency
    buyer_name=NlOrg.objects.get(edrpou=edrpou_num).name
    sellers_dict = {}
    sellers=NlCredit.objects.filter(buyer__edrpou=edrpou_num,ordering_date__year=year).values('seller_id','seller__edrpou','seller__name').distinct()
    if currency == 'UAH':
        sellers=sellers.annotate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by('-sum')
    elif currency == 'EUR':
        sellers=sellers.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by('-sum')
    elif currency == 'USD':
        sellers=sellers.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by('-sum')
    sellers=sellers.filter(sum__isnull=False)
    sellers_list=[]
    period_dates={}
    for m in range(1,13):
        check_period=str(year)+'-'+str(m).zfill(2)
        if NlPeriodPurchases.objects.filter(edrpou=edrpou_num).extra(where=["(to_char(min_date, 'YYYY-MM') <= '"+check_period+"' and to_char(max_date, 'YYYY-MM') >= '"+check_period+"')"]).count() >0:
            period_dates_query=NlPeriodPurchases.objects.filter(edrpou=edrpou_num).extra(where=["(to_char(min_date, 'YYYY-MM') <= '"+check_period+"' and to_char(max_date, 'YYYY-MM') >= '"+check_period+"')"]).values('min_date','max_date','import_date')
            period_dates.update({m:period_dates_query[0]['min_date'].strftime('%d.%m.%Y') +' - '+ period_dates_query[0]['max_date'].strftime('%d.%m.%Y') + ' (import date: ' + period_dates_query[0]['import_date'].strftime('%d.%m.%Y')+ ')'})
        else:
            period_dates.update({m:False})
    #print(period_dates)    
    #totals=[]
    # Total sums
    """for m in range(1,13):
        t_sum=NlCredit.objects.filter(buyer__edrpou=edrpou_num,ordering_date__year=year,ordering_date__month=m)
        if currency == 'UAH':
            t_sum=t_sum.aggregate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))
        elif currency == 'EUR':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))
        elif currency == 'USD':
            t_sum=t_sum.aggregate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))
        totals.append(t_sum['sum'])
    """
    t_sum_q=NlCredit.objects.filter(buyer__edrpou=edrpou_num,ordering_date__year=year).values('buyer_id')
    if currency == 'UAH':
        t_sum_q=t_sum_q.annotate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by()
    elif currency == 'EUR':
        t_sum_q=t_sum_q.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by()
    elif currency == 'USD':
        t_sum_q=t_sum_q.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by()
    t_sum=0
    if t_sum_q:
        t_sum=t_sum_q[0]['sum']

    for b in sellers:
        cur_firm={}
        cur_firm.update({'seller_id':b['seller_id']})
        cur_firm.update({'seller__name':b['seller__name']})
        cur_firm.update({'seller__edrpou':b['seller__edrpou']})
        cur_firm.update({'sum':b['sum']})
        #print (cur_firm['seller__edrpou'])
        b_pms=NlCredit.objects.filter(buyer__edrpou=edrpou_num,seller_id=cur_firm['seller_id'],ordering_date__year=year).annotate(month=TruncMonth('ordering_date')).values('month') 
        if currency == 'UAH':
            b_pms=b_pms.annotate(sum=Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2))).order_by()
        elif currency == 'EUR':
            b_pms=b_pms.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale')))).order_by()
        elif currency == 'USD':
            b_pms=b_pms.annotate(sum=Round(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com')))).order_by()

        pms=[] # per_monnth_summs
        for m in range(1,13):
            pms.append(float(0.0))
        for bb in b_pms:
            bb['month'] = int(str(bb['month'])[5:7])
            pms[bb['month']-1]=bb['sum']
        cur_firm.update({'pms':pms})
        #print(cur_firm)

        sellers_list.append(cur_firm)


    paginator = Paginator(sellers_list, getCurrentRowsPerPage(request))
    page_number = request.GET.get('page')
    try:
        sellers_list = paginator.page(page_number)
    except PageNotAnInteger:
        sellers_list = paginator.page(1)
    except EmptyPage:
        sellers_list = paginator.page(paginator.num_pages) 

    
    #Needs for django template generation
    mnth_list=["Январь","Февраль","Март","Апрель","Май","Июнь","Июль","Август","Сентябрь","Октябрь","Ноябрь","Декабрь"]

    context={
        'sellers_list':sellers_list,
        't_sum':t_sum,
        'edrpou_num':edrpou_num,
        'buyer_name':buyer_name,
        'currency':currency,
        'mnth_list':mnth_list,
        'year':year,
        'YearSelectForm':YearSelectForm,
        'period_dates':period_dates
    }
    context.update({'help_page_id':16})
    return render(request,'inner/PurchasesIndividualFirmShow.html',context)

@login_required(login_url='login')
def PurchasesIndividualFirmRaw(request,edrpou_num,seller_code):
    year=getCurrentYear()
    currency = User.objects.get(username=request.user).profile.currency
    if request.GET.get('selected_year'):
        year=request.GET.get('selected_year')
    raw_records= NlCredit.objects.filter(buyer__edrpou=edrpou_num,seller__edrpou=seller_code,ordering_date__year=year).values('product__name','product__product_code','unit','count','ordering_date')
    if currency == 'UAH':
        raw_records=raw_records.annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).annotate(one_product_cost=Sum(F('one_product_cost')+F('one_product_cost')*0.2)).order_by('ordering_date')
    elif currency == 'EUR':
        raw_records=raw_records.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))).annotate(one_product_cost=Sum((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__eur_mb_sale'))).order_by('ordering_date')
    elif currency == 'USD':
        raw_records=raw_records.annotate(sum=Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))).annotate(one_product_cost=Sum((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__usd_com'))).order_by('ordering_date')

    if request.GET.get('month'):
        raw_records = raw_records.filter(ordering_date__year=year,ordering_date__month=request.GET.get('month'))

    paginator = Paginator(raw_records, getCurrentRowsPerPage(request))
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
        'seller_code':seller_code,
        'raw_records':raw_records,
        'year':year,
    }
    context.update({'help_page_id':16})
    return render(request,'inner/PurchasesIndividualFirmRaw.html',context)

@login_required(login_url='login')
def CompetitorsCatalog(request):
   # https://daruse.ru/prostaya-filtracziya-tabliczyi-na-jquery
    year=getCurrentYear()
    competitors=NlReestr.objects.all().values('seller__edrpou','seller__name','seller__class_field__name')\
            .annotate(total_cost=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2),\
                total_count=Count('one_product_cost')).order_by('-total_cost')
    #print(competitors.query)
    c_importer=list()

    for c in competitors:
        is_importer=False
        if Organisation.objects.filter(edrpou=c['seller__edrpou']).count() > 0:
            is_importer = True 
        c.update({'is_importer': is_importer})

        curr_year_data=False
        if NlReestr.objects.filter(seller__edrpou=c['seller__edrpou'],ordering_date__year=year).count() > 0:
            curr_year_data=True
        c.update({'curr_year_data':curr_year_data})

        c_dates=list()
        for c_per in NlPeriodPurchases.objects.filter(edrpou=c['seller__edrpou']).values('min_date','max_date').order_by('max_date').distinct():
            c_dates.append(c_per['min_date'].strftime('%d-%m-%Y') + " - " + c_per['max_date'].strftime('%d-%m-%Y'))
        c.update({'periods':c_dates})
        
        c_importer.append(c)

    context={
        'horeca_num':0,
        'pack_num':0,
        'food_num':0,
        'other_num':0,
        'competitors':c_importer,
        'year':year,
        }
    context.update({'help_page_id':17})
    return render(request,'inner/CompetitorsCatalog.html',context)

@login_required(login_url='login')
def RecordsSearch(request):
    recSearchForm = RecSearchForm()
    currency = User.objects.get(username=request.user).profile.currency
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=9999
    results=NlReestr.objects.none()

    if request.GET.get('search_string'):
        recSearchForm = RecSearchForm(request.GET)

        results=NlReestr.objects.filter(Q(seller__name__icontains=request.GET.get('search_string')) |Q(seller__edrpou__startswith=request.GET.get('search_string')) | \
            Q(buyer__name__icontains=request.GET.get('search_string')) |Q(buyer__edrpou__startswith=request.GET.get('search_string')) | \
                Q(product__name__icontains=request.GET.get('search_string')) |Q(product__product_code__startswith=request.GET.get('search_string')) )\
                    .values('ordering_date','seller__name','buyer__name','seller__edrpou','buyer__edrpou','product__product_code','product__name','count')
        #print(results.query)
        if currency == 'UAH':
            results=results.annotate(total_cost=Round2(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)),cost=Round2(F('one_product_cost')+F('one_product_cost')*0.2)).order_by('ordering_date')
        elif currency == 'EUR':
            results=results.annotate(total_cost=Round2(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__eur_mb_sale'))),cost=Round2((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__eur_mb_sale'))).order_by('ordering_date')
        elif currency == 'USD':
            results=results.annotate(total_cost=Round2(Sum((F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)/F('exchange__usd_com'))),cost=Round2((F('one_product_cost')+F('one_product_cost')*0.2)/F('exchange__usd_com'))).order_by('ordering_date')
 
    total_sum=0

    for product in results:
        if product['total_cost'] != None:
            total_sum+=product['total_cost']
    total_sum=round(total_sum)

    table = RecordsSearchTable(results)
    RequestConfig(request, paginate={"per_page": num_per_page}).configure(table)
    if request.GET.get('_export'):
        name=request.GET.get('search_string')
        export_format = request.GET.get("_export", None)
        if TableExport.is_valid_format(export_format):
            exporter = TableExport(export_format, table, dataset_kwargs={"title": 'Db_search'})
            return exporter.response(filename='NalogSalesSearch.{0}'.format(export_format)) #
    context={
        'recSearchForm':recSearchForm,
        'total_sum':total_sum,
        'table':table,
        'results':results,
        'currency':currency,
        }
    context.update({'help_page_id':13})
    return render(request,'inner/RecordsSearch.html',context)



@login_required(login_url='login')
def topSalesFirmShow(request,edrpou_num):
    currency = 'UAH'
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    if year == str(db_max_date)[:4]:
        end_date=db_max_date
    period_form=DatesStartEndForm()
    if request.GET.get('start_date'):
        period_form = DatesStartEndForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        period_form = DatesStartEndForm(request.GET)
        end_date=request.GET.get('end_date')
    firm=NlOrg.objects.filter(edrpou = edrpou_num).values('name')[0]['name']
    top_records=NlReestr.objects.filter(Q(seller__edrpou=edrpou_num) & Q(ordering_date__range=[start_date, end_date])).values('product__name','seller__name')\
        .annotate(total_cost=Cast(Round(Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)),IntegerField()),\
                total_count=Cast(Round(Sum('count')),IntegerField())).filter(Q(total_count__gte=100) | Q(total_cost__gte=300000)).order_by('-total_cost')

    table = Top100Table(top_records[:100])
    RequestConfig(request, paginate={"per_page": 100}).configure(table)
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table, dataset_kwargs={"title": '{0}_{1}'.format(start_date,end_date)})
        return exporter.response(filename="topSales_{0}_{1}_{2}_UAH.{3}".format(edrpou_num,start_date,end_date,export_format))
    context={
        'top_records':top_records[:100],
        'period_form': period_form,
        'edrpou_num':edrpou_num,
        'start_date':datetime.datetime.strptime(start_date,"%Y-%m-%d"),
        'end_date':datetime.datetime.strptime(end_date,"%Y-%m-%d"),
        'year':year,  
        'table':table,
        'firm': firm,
        'edrpou_num':edrpou_num,
        'currency':currency,
        }
    help_page_id=19
    context.update({'help_page_id':help_page_id})
    return render(request,'inner/topSalesFirmShow.html',context)
    
    
    
    
    
    
    
    
@login_required(login_url='login')
def RFMIndividual(request):
    YearSelectForm=NlYearSelectForm()
    currency = User.objects.get(username=request.user).profile.currency
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=999
    year=getCurrentYear()
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')
    #print(year)
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
        #print(organisations.query)
    context={
        'organisations':organisations,
        'currency':currency,
        'searchFormOrg':searchFormOrg,
        'YearSelectForm':YearSelectForm,
        'year':year
    }

    context.update({'help_page_id':111})
    return render(request,'inner/RFMIndividual.html',context)


# R
def RClass(x,p,d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]: 
        return 3
    else:
        return 4
    
# F, M
def FMClass(x,p,d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]: 
        return 2
    else:
        return 1

@login_required(login_url='login')
def RFMFirmShow(request,edrpou_num):
    year=getCurrentYear()
    YearSelectForm=NlYearSelectForm()
    if request.GET.get('selected_year'):
        YearSelectForm=NlYearSelectForm(request.GET)
        year=request.GET.get('selected_year')
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=999
    currency = User.objects.get(username=request.user).profile.currency
    seller_name=NlOrg.objects.get(edrpou=edrpou_num).name

    
    connection = pg.connect("host='"+settings.DATABASES['default']['HOST']+"' dbname="+settings.DATABASES['default']['NAME']+" user="+settings.DATABASES['default']['USER']+" password='"+settings.DATABASES['default']['PASSWORD']+"'")
    sql_query='SELECT nlob.edrpou AS buyer_edrpou,nlob.NAME AS buyer_name,ordering_date,reestr_number,SUM (ROUND((one_product_cost*COUNT+one_product_cost*COUNT*0.2) :: NUMERIC,2)) AS "total_pay_cost" FROM nl_reestr LEFT JOIN nl_org nlos ON seller_id=nlos.ID LEFT JOIN nl_org nlob ON buyer_id=nlob.ID WHERE nlos.edrpou='+str(edrpou_num)+' AND nlob.edrpou !=0 AND ordering_date>=\'2020-01-01\' GROUP BY ordering_date,nlob.edrpou,nlob.NAME,reestr_number ORDER BY ordering_date'
    data=pd.read_sql(sql_query, con=connection)
    data['ordering_date']=pd.to_datetime(data['ordering_date'])
    #NOW = datetime.datetime(2021,4,30)
    NOW = datetime.datetime.now()
    # R - Количество дней с последнего заказа F - Количество заказов M - Общая сумма по заказам
    rfmTable = data.groupby('buyer_name').agg({'ordering_date':lambda x:(NOW-x.max()).days, 'reestr_number':lambda x:len(x), 'total_pay_cost':lambda x:x.sum()})
    rfmTable=rfmTable.reset_index()
    rfmTable['ordering_date'] = rfmTable['ordering_date'].astype(int)
    rfmTable=rfmTable.sort_values(by=['total_pay_cost'],ascending=False)
    rfmTable.rename(columns={'ordering_date':'R_recency','reestr_number':'F_frequency','total_pay_cost':'M_monetary_value'}, inplace=True)
    quantiles = rfmTable.quantile(q=[0.25,0.5,0.75]).to_dict()
    rfmsSegmentation = rfmTable
    rfmsSegmentation['R_Quartile'] = rfmsSegmentation['R_recency'].apply(RClass, args=('R_recency',quantiles,))
    rfmsSegmentation['F_Quartile'] = rfmsSegmentation['F_frequency'].apply(FMClass, args=('F_frequency',quantiles,))
    rfmsSegmentation['M_Quartile'] = rfmsSegmentation['M_monetary_value'].apply(FMClass, args=('M_monetary_value',quantiles,))
    # Склеиваем код RFM в одно значение
    rfmsSegmentation['RFMClass'] = rfmsSegmentation.R_Quartile.map(str) \
                            + rfmsSegmentation.F_Quartile.map(str) \
                            + rfmsSegmentation.M_Quartile.map(str)
    print(rfmsSegmentation.columns)
    rfmsSegmentation['M_monetary_value'] = rfmsSegmentation['M_monetary_value'].map(round)
    rfm=rfmsSegmentation.to_dict('records')
    #print(rfm)
    context={
        'edrpou_num':edrpou_num,
        'currency':currency,
        'year':year,
        'seller_name':seller_name,
        'rfm':rfm,
    }
    context.update({'help_page_id':112})
    return render(request,'inner/RFMFirmShow.html',context)

    