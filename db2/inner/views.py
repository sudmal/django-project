from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from urllib.parse import unquote
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import cache_page
import django_tables2 as tables
from django_tables2.export.export import TableExport
from django_tables2.export.views import ExportMixin
from .models import Exchange,Youscore,ReestrStaging,CreditStaging,NlCredit,NlOrg,NlProduct,NlReestr
from django.db.models import Count, Sum, Q, Avg, Subquery, OuterRef, F, FloatField, Max
from .forms import SearchFormOrg
import datetime
import requests
import json 

from django.contrib.postgres.aggregates import ArrayAgg
from django_tables2 import RequestConfig


# if now is not jan or feb, year is current year, other way - previus
year = str((datetime.date.today() - datetime.timedelta(days=59)).year)

def logUserData(request):
    print(request.META['REMOTE_ADDR'])

def autocomplete_tm(request):
    titles = list()
    return JsonResponse(titles, safe=False)

def sales_autocomplete_org(request):
    titles = list()
    if 'term' in request.GET:
        found_org = NlReestr.objects.filter(Q(seller__name__icontains=request.GET.get('term')) |Q(seller__edrpou__startswith=request.GET.get('term')) )\
            .values('seller__name').annotate(sum=Sum(F('one_product_cost')*F('count')+F('one_product_cost')*F('count')*0.2)).distinct().order_by('-sum')
        print(found_org.query)
        for tm in found_org:
            print(tm)
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
 

    context={
        'year':year,
    }
    return render(request,'inner/test.html',context)

@login_required(login_url='login')
def SalesIndividual(request):
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    searchFormOrg=SearchFormOrg()
    organisations=[]
    if request.GET.get('search_string'):
        searchFormOrg = SearchFormOrg(request.GET)
        organisations=NlReestr.objects.filter(Q(seller__name__icontains=request.GET.get('search_string'))|Q(seller__edrpou__icontains=request.GET.get('search_string')))\
            .values('seller__name','seller__edrpou').distinct()
        #print(organisations.query)
    context={
        'organisations':organisations,
        'searchFormOrg':searchFormOrg,
    }
    return render(request,'inner/SalesIndividual.html',context)