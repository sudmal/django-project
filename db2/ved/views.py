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
from .models import Competitors
from .models import Organisation,GtdRecords,Records,Trademark,Sender,Country,TnvedGroup,Exchange,filter_codes,TnvedGroup,Youscore,RecordsStaging,RecordsCompetitors
from .forms import SearchForm,SearchFormOrg
from .tables import CompetitorsComparsePeriodDetailTable
from django.db.models import Count, Sum, Q, Avg, Subquery, OuterRef, F, FloatField, Max
import datetime
import requests
import json 
import hashlib
from django.core.cache import caches

from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.auth.models import User
from django_tables2 import RequestConfig


## https://dizballanze.com/ru/django-project-optimization-part-3/
#cache = caches['default']  # `default` is a key from CACHES dict in settings.py
#cache.clear()


# if now is not jan or feb, year is current year, other way - previus
year = str((datetime.date.today() - datetime.timedelta(days=120)).year)

def logUserData(request):
    print(request.META['REMOTE_ADDR'])

def autocomplete_tm(request):
    titles = list()
    if 'term' in request.GET:
        found_trademarks = GtdRecords.objects.filter(trademark__name__icontains=request.GET.get('term'))\
            .values('trademark__name').annotate(sum=Sum('cost_fact')).distinct().order_by('-sum')[:10]
        for tm in found_trademarks:
            titles.append(tm['trademark__name'])
    if len(titles)==0:
        titles.append("Ничего не найдено")
    return JsonResponse(titles, safe=False)

def autocomplete_org(request):
    titles = list()
    if 'term' in request.GET:
        found_trademarks = GtdRecords.objects.filter(Q(record__recipient__firm_alias__icontains=request.GET.get('term')) |Q(record__recipient__name__icontains=request.GET.get('term')) | Q(record__recipient__edrpou__startswith=request.GET.get('term')) )\
            .values('record__recipient__name').annotate(sum=Sum('cost_fact')).distinct().order_by('-sum')[:10]
        for tm in found_trademarks:
            titles.append(tm['record__recipient__name'])
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
    rec_dates = Records.objects.distinct('date__year','date__month').values('date')
    dates=[]
    for rd in rec_dates:
        dates.append(str(rd['date'])[0:7])
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,dates)))))
    dates_dict={}
    for y in sorted(years,reverse=True):
        dates_dict[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in dates:
                dates_dict[y][m]=True
            else:
                dates_dict[y][m]=False
    return dates_dict

def generateOrder(request,default_sort_order,default_sort_field):
    # setting up defaults
    sort_order=default_sort_order
    sort_field=default_sort_field
    sort_order_symbol=''
    if default_sort_order=='desc':
        sort_order_symbol='-'
    
    # Если в request.GET присутствует параметр sort_order (была нажата кнопка) - 
    # меняем порядок сортировки на противоположный
    # change sort order for link and generate symbol for current query
    if request.GET.get('sort_order'):
        if request.GET.get('sort_order')=='asc':
            sort_order='desc'  # next link status 
            sort_order_symbol='-' # current query
        if request.GET.get('sort_order')=='desc':
            sort_order='asc'  # next link status
            sort_order_symbol='' # current query
            
    print (sort_order)
    # Если в request.GET присутствует параметр sort_field (была нажата кнопка) - 
    # устанавливаем текущее поле для сортировки
    if request.GET.get('sort_field'):
        sort_field=request.GET.get('sort_field')
    order={'sort_order_symbol':sort_order_symbol,'sort_order':sort_order,'sort_field':sort_field}
    return order


@login_required(login_url='login')
def index(request):
    return render(request,'ved/index.html')

@login_required(login_url='login')
def test(request):
    order=generateOrder(request,'asc','competitor_code')
    competitors_all=Competitors.objects.all().order_by(order['sort_order_symbol']+order['sort_field'])
    paginator = Paginator(competitors_all, 20)
    page_number = request.GET.get('page')
    try:
        competitors = paginator.page(page_number)
    except PageNotAnInteger:
        competitors = paginator.page(1)
    except EmptyPage:
        competitors = paginator.page(paginator.num_pages) 

    context={
        'year':year,
        'table_data': competitors,
        'order':order,
    }
    return render(request,'ved/test.html',context)


def Youscore_get(competitors_top):
    api_key='1f0900000ebe229bcca6e39128b59d5be1fa2bb7'
    fin_data={}
    ved_data={}

    ###########
    year=2019 #
    ###########

    for c_top in competitors_top:
        edrpou=c_top['record__recipient__edrpou']
        # Must be only 2019 year in test period
        # ysr="https://api.youscore.com.ua/v1/financialIndicators/"+str(edrpou)+"/years/"+str(int(year)-1)+"?apiKey="+api_key
        ysr="https://api.youscore.com.ua/v1/financialIndicators/"+str(edrpou)+"/years/"+str(year)+"?apiKey="+api_key
        #print(ysr)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}
        ret_fin=''
        ret_ved=''
        if Youscore.objects.filter(request=ysr):
            #print("Get finanace youscore data from cache")
            db_reply=Youscore.objects.filter(request=ysr).values('jsonreply')

            ret_fin=str(db_reply[0]['jsonreply'])
            #print(ret_fin)
        else:
            #print("Get finance youscore data from Youscore API")
            result = requests.get(ysr, headers=headers)
            save_result=Youscore.objects.create(request=ysr,jsonreply=result.text)
            ret_fin=str(result.text)
        #https://api.youscore.com.ua/v1/externalEconomies/38797324?apiKey=1f0900000ebe229bcca6e39128b59d5be1fa2bb7
        #https://api.youscore.com.ua/v1/externalEconomies/38797324?year=2020&apiKey=1f0900000ebe229bcca6e39128b59d5be1fa2bb7
                
        ysr="https://api.youscore.com.ua/v1/externalEconomies/"+str(edrpou)+"?year="+str(int(year))+"&apiKey="+api_key
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'}
        
        if Youscore.objects.filter(request=ysr):
            db_reply=Youscore.objects.filter(request=ysr).values('jsonreply')
            #print(db_reply)
            ret_ved=str(db_reply[0]['jsonreply'])
 # Uncomment if we get full youscore account
 #       else:
 #           print("Get youscore data from API")
 #           result = requests.get(ysr, headers=headers)
 #           if result:
 #               print("Save youscore data from API to cache")
 #               save_result=Youscore.objects.create(request=ysr,jsonreply=result.text)
 #               ret_ved=str(result.text)
        if len(ret_fin) > 0:
            fin_data.update({edrpou:json.loads(ret_fin)})
        if len(ret_ved) > 0:
            ved_data.update({edrpou:json.loads(ret_ved)})
    ret_dict={
        'fin':fin_data,
        'ved':ved_data,
    }
    #print(ret_dict['fin']) 
    return ret_dict

@login_required(login_url='login')
def CompetitorsComparse(request):
    help_page_id = 8
    search_form = SearchForm()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    end_date_q=str(Records.objects.filter(date__range=[start_date, end_date]).aggregate(Max('date'))['date__max'])
    #print(end_date_q)
    if end_date_q:
        end_date=end_date_q
    dates=getRecDates()
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    prev_start_date=str(int(year)-1)+start_date[4:10]
    prev_end_date=str(int(year)-1)+end_date[4:10]
    

    comparse = GtdRecords.objects.filter(Q(record__recipient__edrpou__in=Competitors.objects.values_list('competitor_code',flat=True)) & \
        Q(record__date__range=[start_date, end_date] ))\
        .extra(where=["LEFT(product_code::text,8) IN (SELECT LEFT(gcodes,8) from tnved_group)"])\
            .values('record__recipient__edrpou','record__recipient__name')\
                .annotate(total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')),count=Count('cost_fact',distinct=True),total_cost=Sum('cost_fact')).order_by('-total_cost')
    #print(str(comparse.query))

    m = hashlib.md5()
    m.update(str(comparse.query).encode('utf-8'))
    queryhache=m.hexdigest()
    comparse_prev = GtdRecords.objects.filter(Q(record__recipient__edrpou__in=Competitors.objects.values_list('competitor_code',flat=True)) & \
        Q(record__date__range=[prev_start_date, prev_end_date] ))\
        .extra(where=["LEFT(product_code::text,8) IN (SELECT LEFT(gcodes,8) from tnved_group)"])\
            .values('record__recipient__edrpou').annotate(total_cost=Sum('cost_fact'))
    
    
    total_sum=0
    edrpou_list=[]
    comparse_list=[]
    for e in comparse:
        edrpou_list.append(e['record__recipient__edrpou'])


    for c in comparse:
        total_sum+=c['total_cost']
 

    comparse2=comparse.annotate(percent=(F('total_cost')/total_sum)*100)
    for c in comparse2:
        delta=0
        prev_total_cost=0
        for c2 in comparse_prev:
            if c2['record__recipient__edrpou'] in edrpou_list:
                if c2['record__recipient__edrpou'] == c['record__recipient__edrpou']:
                    delta = round(float(c['total_cost'])-float(c2['total_cost']),2)
                    prev_total_cost = c2['total_cost']
        c['delta'] = delta 
        c['prev_total_cost'] = prev_total_cost
        comparse_list.append(c)


    # pie chart variables
    data=[]
    labels=[]
    for c in comparse_list[:10]:
        labels.append(getFirmName(c['record__recipient__name']))
        data.append(round(c['percent'],1))
    labels.append('Другие')
    data.append(round(100-sum(data),1))
    context = {
        'help_page_id':help_page_id,
        'dates': dates,
        'labels': labels,
        'data': data,
        'queryhache':queryhache,
        'comparse': comparse_list,
        'start_date':start_date,
        'end_date':end_date,
        'search_form':search_form
        }
    return render(request,'ved/CompetitorsComparse.html',context)

@login_required(login_url='login')
@user_passes_test(lambda u: u.profile.ved_part, login_url='/')
def IndividualReport(request):
    order=generateOrder(request,'desc','total_cost')
    help_page_id = 7
    context=dict()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    search_form_org = SearchFormOrg()
    dates=getRecDates()
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=99999999999
    if request.GET.get('start_date'):
        search_form_org = SearchFormOrg(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form_org = SearchFormOrg(request.GET)
        end_date=request.GET.get('end_date')
  
    if request.GET.get('search_string'):
        search_form_org = SearchFormOrg(request.GET)
        grecords_all = GtdRecords.objects.filter((Q(record__recipient__edrpou__startswith=request.GET.get('search_string')) | \
             Q(record__recipient__name__icontains=request.GET.get('search_string'))) & Q(record__date__range=[start_date, end_date]))\
                .values('record__recipient__edrpou','record__recipient__name','record__recipient__is_competitor')\
                 .annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'),total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')), tms_count=Count('trademark__name',distinct=True))\
                     .order_by(order['sort_order_symbol']+order['sort_field'])
        #print(grecords_all.query)
        paginator = Paginator(grecords_all, num_per_page)
        page_number = request.GET.get('page')
        try:
            grecords = paginator.page(page_number)
        except PageNotAnInteger:
            grecords = paginator.page(1)
        except EmptyPage:
            grecords = paginator.page(paginator.num_pages) 

        context = {
            "search_string": request.GET.get('search_string'),
            "grecords": grecords,
            "start_date": request.GET.get('start_date'),
            "end_date": request.GET.get('end_date'),
        }
    ## ADD CONTEXT VARIABLES HERE 
    context.update({'start_date':start_date})
    context.update({'end_date':end_date})
    context.update({'help_page_id':help_page_id})
    context.update({"search_form_org": search_form_org})
    context.update({'dates': dates})
    context.update({'request':request})
    context.update({'order':order})

    return render(request,'ved/IndividualReport.html',context)

@login_required(login_url='login')
def IndividualReportFirmShow(request,edrpou_num):
    help_page_id = 7
    order=generateOrder(request,'asc','record__date')
    context=dict()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    dates=getRecDates()
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=99999999999
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    if edrpou_num >= 0:
        firm=Organisation.objects.get(edrpou = edrpou_num)
        queryset_list = GtdRecords.objects.filter((Q(record__recipient__edrpou=edrpou_num) & Q(record__date__range=[start_date, end_date])))\
            .values('record__date','record__gtd_name').order_by('record__date')\
                .annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'),\
                    total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')),tms=ArrayAgg('trademark__name', distinct=True))\
                    .order_by(order['sort_order_symbol']+order['sort_field'])
        paginator = Paginator(queryset_list, num_per_page)
        page_number = request.GET.get('page')
        try:
            queryset = paginator.page(page_number)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        context = {
            'firm' : firm,
            'help_page_id':help_page_id,
            "edrpou_detail": edrpou_num,
            "dates": dates,
            'report': queryset,
            'start_date': request.GET['start_date'], 
            'end_date':request.GET['end_date']
            }
        context.update({'order':order})
        return render(request,'ved/IndividualReportFirmShow.html',context)
    else:
        return HttpResponse('EDRPOU {0} IS NOT VALID.<br><a href="/">  - Go back</a>'.format(edrpou_num))

@login_required(login_url='login')
def IndividualReportRaw(request,edrpou_num,gtd_num):
    help_page_id=7
    order=generateOrder(request,'asc','record__date')
    logUserData(request)
    context=dict()
    dates=getRecDates()
    gtd=unquote(gtd_num)
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=99999999999
    firm=Organisation.objects.get(edrpou = edrpou_num)
    queryset_list = GtdRecords.objects.filter((Q(record__recipient__edrpou=edrpou_num) & Q(record__gtd_name=gtd)))\
            .values('record__sender__name','record__sender__country__name','record__date','product_code','trademark__name','description','cost_fact')\
                .annotate(total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact'))).order_by(order['sort_order_symbol']+order['sort_field'])
    paginator = Paginator(queryset_list, num_per_page)
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)
    context = {
                "firm" : firm,
                "help_page_id":help_page_id,
                'start_date': request.GET['start_date'], 
                'end_date':request.GET['end_date'],
                'dates' : dates,
                'records': records,
                'gtd': gtd,
                'edrpou_num':edrpou_num,
                'order':order,
            }
    return render(request,'ved/IndividualReportRaw.html',context)

@login_required(login_url='login')
def TrademarkReportSearch(request):
    help_page_id=9
    order=generateOrder(request,'desc','total_cost')
    context=dict()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    search_form = SearchForm()
    dates=getRecDates()
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    if request.GET.get('search_string'):
        search_form = SearchForm(request.GET)
        grecords_all = GtdRecords.objects.filter((Q(trademark__name__icontains=request.GET.get('search_string')) & Q(record__date__range=[start_date, end_date])))\
           .values('trademark__name').annotate(count=Count("product_code"),total_cost=Sum('cost_fact'),\
               total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact'))).order_by(order['sort_order_symbol']+order['sort_field'])
        context = {
                'grecords_all': grecords_all,
                'search_form': search_form,
                'start_date': request.GET['start_date'],
                'end_date':request.GET['end_date'],
        }
    context.update({"search_form": search_form})
    context.update({'dates': dates})
    context.update({'help_page_id':help_page_id})
    context.update({'order':order})
    return render(request,'ved/TMReportSearch.html',context)

@login_required(login_url='login')
def TrademarkReportShow(request,trademark_name):
    help_page_id=9
    order=generateOrder(request,'desc','total_cost')
    context=dict()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    dates=getRecDates()
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    if  trademark_name:
        trademark_name=unquote(trademark_name)
        context.update({'trademark_name':trademark_name})
        queryset_list1 = GtdRecords.objects.filter((Q(trademark__name=trademark_name) & Q(record__date__range=[start_date, end_date])))\
           .values('record__recipient__edrpou','record__recipient__name').annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'),\
               total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact'))).order_by(order['sort_order_symbol']+order['sort_field'])
        total_sum=0
        for c in queryset_list1:
            total_sum+=c['total_cost']
        queryset_list=queryset_list1.annotate(percent=(F('total_cost')/total_sum)*100)
        context.update({'queryset_list':queryset_list})
    competitors=list(Competitors.objects.values_list('competitor_code',flat=True))
    context.update({'competitors':competitors})
    context.update({'request':request})
    context.update({'help_page_id':help_page_id})
    context.update({'order':order})
    return render(request,'ved/TMReportShow.html',context)

@login_required(login_url='login')
def TrademarkReportRaw(request,trademark_name,edrpou_num):
    order=generateOrder(request,'asc','record__date')
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=99999999999
    context=dict()
    dates=getRecDates()
    trademark_name=unquote(trademark_name)
    firm=Organisation.objects.get(edrpou = edrpou_num)
    queryset_list = GtdRecords.objects.filter(Q(record__recipient__edrpou=edrpou_num) & Q(trademark__name=trademark_name) & Q(record__date__range=[start_date, end_date]))\
            .values('record__sender__name','record__sender__country__name','record__date','product_code','description','cost_fact')\
                .annotate(cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact'))).order_by(order['sort_order_symbol']+order['sort_field'])
    summ = GtdRecords.objects.filter(Q(record__recipient__edrpou=edrpou_num) & Q(trademark__name=trademark_name) & Q(record__date__range=[start_date, end_date]))\
                .aggregate(cost_usd=Sum('cost_fact'))
    tm_firm_summ=summ['cost_usd']
    paginator = Paginator(queryset_list, num_per_page)
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)
    context = {
                "firm" : firm,
                'start_date': request.GET['start_date'], 
                'end_date':request.GET['end_date'],
                'dates' : dates,
                'records': records,
                'trademark_name': trademark_name,
                'edrpou_num':edrpou_num,
                'tm_firm_summ':tm_firm_summ,
                'order':order,
            }
    help_page_id=9
    context.update({'help_page_id':help_page_id})
    return render(request,'ved/TMReportRaw.html',context)

@login_required(login_url='login')
def HRKReport(request):
    report_percent=80
    if request.GET.get('report_percent'):
        report_percent=request.GET.get('report_percent')
    search_form=SearchForm()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    dates=getRecDates()
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    tnved_group=TnvedGroup.objects.all()
    gcodes_all=list(set(list(tnved_group.values_list('gcodes', flat=True))))
    full_group_summ=GtdRecords.objects.filter(record__date__range=[start_date, end_date]).values('cost_fact')\
            .extra(where=["LEFT(product_code::text,8) IN (\'"+("\',\'".join(gcodes_all))+"\')"]).aggregate(Sum('cost_fact'))
    full_group_summ_n=full_group_summ['cost_fact__sum']
    gpercents=[]
    glabels=[]
    for gid in list(set(list(tnved_group.values_list('id', flat=True)))):
        current_gcodes=TnvedGroup.objects.filter(id=gid).values('gcodes')
        gcodes=list(set(list(current_gcodes.values_list('gcodes', flat=True))))
        cur_gname=TnvedGroup.objects.filter(id=gid).distinct()
        cur_group_summ=GtdRecords.objects.filter(record__date__range=[start_date, end_date]).values('cost_fact')\
            .extra(where=["LEFT(product_code::text,8) IN (\'"+("\',\'".join(gcodes))+"\')"]).aggregate(Sum('cost_fact'))
        percent=round((cur_group_summ['cost_fact__sum']/full_group_summ_n)*100,0)
        gpercents.append(int(percent))
        glabels.append(str(cur_gname.values_list('gname',flat=True)[0]))
    comparse = GtdRecords.objects.filter(Q(record__date__range=[start_date, end_date]) & Q(cost_fact__gt=0))\
        .extra(where=["LEFT(product_code::text,8) IN (SELECT LEFT(gcodes,8) from tnved_group)"])\
            .values('record__recipient__edrpou','record__recipient__name')\
                .annotate(total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')),\
                    count=Count('cost_fact',distinct=True),total_cost=Sum('cost_fact')).order_by('-total_cost')
    
    total_sum=0.0
    num_to_show=0
    percents_sum=0.0
    for c in comparse:
        total_sum+=c['total_cost']
    for c in comparse:
        if percents_sum < total_sum*float(report_percent)/100:
            percents_sum+= c['total_cost']
            num_to_show+=1
    comparse2=comparse.annotate(percent=(F('total_cost')/total_sum)*100)[:num_to_show]

    # pie chart variables
    data=[]
    labels=[]
    for c in comparse2[:10]:
        if len(c['record__recipient__name'])>50:
            labels.append(c['record__recipient__name'][:50]+"...")
        else:
            labels.append(c['record__recipient__name'])
        data.append(round(c['percent'],1))
    labels.append('Другие')
    data.append(round(100-sum(data),1))
    competitors=list(Competitors.objects.values_list('competitor_code',flat=True))
    context = {
        'total_sum': total_sum,
        'percents_sum': percents_sum,
        'dates': dates,
        'labels': labels,
        'data': data,
        'comparse': comparse2,
        'search_form': search_form,
        'start_date':start_date,
        'end_date':end_date,
        'gpercents':gpercents,
        'glabels':glabels,
        'report_percent':report_percent,
        'num_to_show':num_to_show,
        'competitors':competitors,
        }
    help_page_id=10
    context.update({'help_page_id':help_page_id})
    return render(request,'ved/HRKReport.html',context)

def CompetitorsCatalog(request):
    help_page_id=4
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    max_year_date=Records.objects.filter(Q(date__range=[start_date, end_date])).latest('date').date
    max_yearprev_date=Records.objects.filter(Q(date__range=[start_date, end_date])).latest('date').date
 
    competitors=GtdRecords.objects.filter(Q(record__recipient__edrpou__in=Competitors.objects.all().values('competitor_code')))\
        .values('record__recipient__edrpou','record__recipient__name','record__recipient__firm_alias')\
            .annotate(total_cost=Sum('cost_fact'),total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')),\
                total_count=Count('cost_fact')).order_by('-total_cost')
    competitors_top=competitors[:42]
    yresults_dict={}
    yresult=Youscore_get(competitors_top)
    #print(yresult['ved'])
    competitors_list=[]
    #print(yresult['fin'])
    for e in  yresult['fin']:
        #print (e)
        money_in=''
        utkved=[]
        #print (yresult['fin'][e].keys())
        if 'indicators' in yresult['fin'][e].keys():
            for f in yresult['fin'][e]['indicators']:
                if f['field'] == 'Разом доходи' or f['field'] == 'Валовий: прибуток' :
                    money_in=str(f['min'])+"-"+str(f['max'])
            for f in yresult['ved'][e]['topImportUktZed']:
                utkved.append(str('<b>'+f['uktZed'])+'</b> - '+str(f['description']))

            yresults_dict.update({  e:
                                        {
                                            'fin':{
                                                'money_in': money_in,
                                            },
                                            'ved':{
                                                'utkved': utkved,
                                            }

                                        }
                                })

    edrpou_list=[]
    for e in yresults_dict:
        edrpou_list.append(e)
    for c in competitors:
        money_in=''
        utk_top=''
        for y in yresults_dict:
            if c['record__recipient__edrpou'] in edrpou_list:
                if str(y) == str(c['record__recipient__edrpou']):
                    money_in=yresults_dict[y]['fin']['money_in']
                    utk_top=yresults_dict[y]['ved']['utkved']
        c['y_fin_m_in'] = money_in
        c['y_ved_utk'] = utk_top
        competitors_list.append(c)
    context={
        'help_page_id':help_page_id,
        'yresults': yresults_dict,
        'competitors':competitors_list,
        'start_date':start_date,
        'end_date':end_date,
        'year':year,
        }
    return render(request,'ved/CompetitorsCatalog.html',context)

def ProductCodesCatalog(request):
    help_page_id=5
    ProductCodes=filter_codes.objects.all()
    context={
        'ProductCodes':ProductCodes,
        'help_page_id':help_page_id,
        }
    return render(request,'ved/ProductCodesCatalog.html',context)

def TnvedGroupCatalog(request):
    TnvedGroupData=TnvedGroup.objects.values('gname').distinct().annotate(codes=ArrayAgg('gcodes')).order_by('gname')
    context={
        'TnvedGroup':TnvedGroupData,
        'help_page_id':6,
        }
    return  render(request, 'ved/TnvedGroupCatalog.html', context)

def CompetitorsCatalogPeriodDetail(request,edrpou_num):
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    search_form=SearchForm()
    dates=getRecDates()
    num_per_page = User.objects.get(username=request.user).profile.rows_per_page
    if num_per_page==0:
        num_per_page=99999999999
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    firm=Organisation.objects.get(edrpou = edrpou_num)
 
    period_summ = str(RecordsCompetitors.objects.filter(recipient_code=edrpou_num,date__range=[start_date, end_date]).aggregate(Sum('cost_fact'))['cost_fact__sum'])
    #print(period_summ)
    CompetitorsDetailRaw = RecordsCompetitors.objects.filter(Q(recipient_code=edrpou_num) & Q(date__range=[start_date, end_date])).values('date','gtd','country', 'sender_name', 'recipient_name','recipient_code','product_code','trademark','description','cost_fact','cost_customs').order_by('date')
    if request.GET.get('SearchString'):
        #print("additional filtering by string "+request.GET.get('SearchString'))
        CompetitorsDetailRaw = CompetitorsDetailRaw.filter(Q(description__icontains=request.GET.get('SearchString')) | Q(trademark__icontains=request.GET.get('SearchString')) | Q(gtd__icontains=request.GET.get('SearchString'))| Q(product_code__icontains=request.GET.get('SearchString')) )
        print(CompetitorsDetailRaw)
    table = CompetitorsComparsePeriodDetailTable(CompetitorsDetailRaw)
    RequestConfig(request, paginate={"per_page": num_per_page}).configure(table)
    export_format = request.GET.get("_export", None)
    if TableExport.is_valid_format(export_format):
        exporter = TableExport(export_format, table, dataset_kwargs={"title": firm.name})
        return exporter.response(filename="VEDImport_{0}_{1}_{2}.{3}".format(edrpou_num,start_date,end_date,export_format))
    context={
        'search_form': search_form,
        'SearchString': request.GET.get('SearchString'),
        'edrpou_num':edrpou_num,
        'start_date':start_date,
        'end_date':end_date,
        'year':year,  
        'dates':dates,
        'table':table,
        'period_summ':period_summ,
        'firm': firm,
        'edrpou_num':edrpou_num,
        }
    help_page_id=4
    context.update({'help_page_id':help_page_id})
    return  render(request, 'ved/CompetitorsCatalogPeriodDetail.html', context)

