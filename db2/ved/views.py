from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from urllib.parse import unquote
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from .models import Competitors
from .models import Organisation,GtdRecords,Records,Trademark,Sender,Country,TnvedGroup,Exchange
from .forms import SearchForm
from django.db.models import Count, Sum, Q, Avg, Subquery, OuterRef, F, FloatField
import datetime

from django.contrib.postgres.aggregates import ArrayAgg


# if now is not jan or feb, year is current year, other way - previus
year = str((datetime.date.today() - datetime.timedelta(days=59)).year)

def logUserData(request):
    print(request.META['REMOTE_ADDR'])

def getRecDates():
    rec_dates = Records.objects.distinct('date__month').values('date')
    dates=[]
    for rd in rec_dates:
        dates.append(str(rd['date'])[0:7])
    return dates

@login_required(login_url='login')
def index(request):
    return render(request,'ved/index.html')


@login_required(login_url='login')
def CompetitorsComparse(request):
    logUserData(request)
    search_form = SearchForm()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    rec_dates = getRecDates()
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,rec_dates)))))
    dates={}
    for y in years:
        dates[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in rec_dates:
                dates[y][m]=True
            else:
                dates[y][m]=False
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    comparse = GtdRecords.objects.filter(Q(record__recipient__edrpou__in=Competitors.objects.values_list('competitor_code',flat=True)) & \
        Q(record__date__range=[start_date, end_date] ))\
        .extra(where=["LEFT(product_code::text,8) IN (SELECT LEFT(gcodes,8) from tnved_group)"])\
            .values('record__recipient__edrpou','record__recipient__name')\
                .annotate(total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')),count=Count('cost_fact',distinct=True),total_cost=Sum('cost_fact')).order_by('-total_cost')
                # ,total_cost_eur=Sum(F('cost_fact') * F('record__date__usd_nbu') / F('record__date__eur_nbu'), output_field=FloatField()
    total_sum=0
    for c in comparse:
        total_sum+=c['total_cost']
    comparse2=comparse.annotate(percent=(F('total_cost')/total_sum)*100)

    # pie chart variables
    data=[]
    labels=[]
    for c in comparse2[:10]:
        labels.append(c['record__recipient__name'])
        data.append(round(c['percent'],1))
    labels.append('Другие')
    data.append(round(100-sum(data),1))
    context = {
        'dates': dates,
        'labels': labels,
        'data': data,
        'comparse': comparse2,
        'start_date':start_date,
        'end_date':end_date,
        'search_form':search_form
        }
    return render(request,'ved/CompetitorsComparse.html',context)



@login_required(login_url='login')
def test(request):
    logUserData(request)
    rec_dates = getRecDates()
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,rec_dates)))))
    dates={}
    for y in years:
        dates[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in rec_dates:
                dates[y][m]=True
            else:
                dates[y][m]=False
    context = {
        'dates': dates,
        }
    return render(request,'ved/test.html',context)

@login_required(login_url='login')
def IndividualReport(request):
    logUserData(request)
    context=dict()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    search_form = SearchForm()
    rec_dates = getRecDates()
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,rec_dates)))))
    dates={}
    for y in years:
        dates[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in rec_dates:
                dates[y][m]=True
            else:
                dates[y][m]=False
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    if request.GET.get('search_string'):
        search_form = SearchForm(request.GET)
        grecords_all = GtdRecords.objects.filter((Q(record__recipient__edrpou__startswith=request.GET.get('search_string')) | \
             Q(record__recipient__name__icontains=request.GET.get('search_string'))) & Q(record__date__range=[start_date, end_date]))\
                .values('record__recipient__edrpou','record__recipient__name','record__recipient__is_competitor')\
                 .annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'),total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')), tms_count=Count('trademark__name',distinct=True),\
                     tms=ArrayAgg('trademark__name', distinct=True)).order_by('-total_cost')

        paginator = Paginator(grecords_all, 10)
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
    context.update({"search_form": search_form})
    context.update({'dates': dates})
    return render(request,'ved/IndividualReport.html',context)

@login_required(login_url='login')
def IndividualReportFirmShow(request,edrpou_num):
    context=dict()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    rec_dates = getRecDates()
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,rec_dates)))))
    dates={}
    for y in years:
        dates[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in rec_dates:
                dates[y][m]=True
            else:
                dates[y][m]=False
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
                .annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'),total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')),tms=ArrayAgg('trademark__name', distinct=True))
        paginator = Paginator(queryset_list, 50)
        page_number = request.GET.get('page')
        try:
            queryset = paginator.page(page_number)
        except PageNotAnInteger:
            queryset = paginator.page(1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        context = {
            "firm" : firm,
            "edrpou_detail": edrpou_num,
            "dates": dates,
            'report': queryset,
            'start_date': request.GET['start_date'], 
            'end_date':request.GET['end_date']
            }
        return render(request,'ved/IndividualReportFirmShow.html',context)
    else:
        return HttpResponse('EDRPOU {0} IS NOT VALID.<br><a href="/">  - Go back</a>'.format(edrpou_num))

@login_required(login_url='login')
def IndividualReportRaw(request,edrpou_num,gtd_num):
    logUserData(request)
    context=dict()
    rec_dates = getRecDates()
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,rec_dates)))))
    dates={}
    for y in years:
        dates[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in rec_dates:
                dates[y][m]=True
            else:
                dates[y][m]=False
    gtd=unquote(gtd_num)
    firm=Organisation.objects.get(edrpou = edrpou_num)
    queryset_list = GtdRecords.objects.filter((Q(record__recipient__edrpou=edrpou_num) & Q(record__gtd_name=gtd)))\
            .values('record__sender__name','record__sender__country__name','record__date','product_code','trademark__name','description','cost_fact')\
                .annotate(cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')),).order_by('record__date')
    paginator = Paginator(queryset_list, 10)
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)
    context = {
                "firm" : firm,
                'start_date': request.GET['start_date'], 
                'end_date':request.GET['end_date'],
                'dates' : dates,
                'records': records,
                'gtd': gtd,
                'edrpou_num':edrpou_num,
            }
    return render(request,'ved/IndividualReportRaw.html',context)

@login_required(login_url='login')
def TrademarkReportSearch(request):
    context=dict()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    search_form = SearchForm()
    rec_dates = getRecDates()
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,rec_dates)))))
    dates={}
    for y in years:
        dates[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in rec_dates:
                dates[y][m]=True
            else:
                dates[y][m]=False
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    if request.GET.get('search_string'):
        search_form = SearchForm(request.GET)
        grecords_all = GtdRecords.objects.filter((Q(trademark__name__icontains=request.GET.get('search_string')) & Q(record__date__range=[start_date, end_date])))\
           .values('trademark__name').annotate(count=Count("product_code"),total_cost=Sum('cost_fact')).order_by('-total_cost')
        context = {
                'grecords_all': grecords_all,
                'search_form': search_form,
                'start_date': request.GET['start_date'],
                'end_date':request.GET['end_date'],
        }
    context.update({"search_form": search_form})
    context.update({'dates': dates})
    return render(request,'ved/TMReportSearch.html',context)

def TrademarkReportShow(request,trademark_name):
    context=dict()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    rec_dates = getRecDates()
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,rec_dates)))))
    dates={}
    for y in years:
        dates[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in rec_dates:
                dates[y][m]=True
            else:
                dates[y][m]=False
    if request.GET.get('start_date'):
        search_form = SearchForm(request.GET)
        start_date=request.GET.get('start_date')
    if request.GET.get('end_date'):
        search_form = SearchForm(request.GET)
        end_date=request.GET.get('end_date')
    if  trademark_name:
        trademark_name=unquote(trademark_name)
        context.update({'trademark_name':trademark_name})
        queryset_list = GtdRecords.objects.filter((Q(trademark__name=trademark_name) & Q(record__date__range=[start_date, end_date])))\
           .values('record__recipient__edrpou','record__recipient__name').annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'),\
               total_cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact'))).order_by('-total_cost')
        context.update({'queryset_list':queryset_list})
    competitors=list(Competitors.objects.values_list('competitor_code',flat=True))
    context.update({'competitors':competitors})
    return render(request,'ved/TMReportShow.html',context)

def TrademarkReportRaw(request,trademark_name,edrpou_num):
    logUserData(request)
    context=dict()
    rec_dates = getRecDates()
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,rec_dates)))))
    dates={}
    for y in years:
        dates[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in rec_dates:
                dates[y][m]=True
            else:
                dates[y][m]=False
    trademark_name=unquote(trademark_name)
    firm=Organisation.objects.get(edrpou = edrpou_num)
    queryset_list = GtdRecords.objects.filter((Q(record__recipient__edrpou=edrpou_num) & Q(trademark__name=trademark_name)))\
            .values('record__sender__name','record__sender__country__name','record__date','product_code','description','cost_fact')\
                .annotate(cost_eur=Sum((F('record__exchange__usd_nbu')/F('record__exchange__eur_nbu'))*F('cost_fact')),).order_by('record__date')
    paginator = Paginator(queryset_list, 10)
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
            }
    return render(request,'ved/TMReportRaw.html',context)

@login_required(login_url='login')
def HRKReport(request):
    report_percent=80
    if request.GET.get('report_percent'):
        report_percent=request.GET.get('report_percent')
    search_form=SearchForm()
    start_date=year+'-01-01'
    end_date=year+'-12-31'
    rec_dates = getRecDates()
    get_years=lambda x: str(x)[:4]
    years=(list(set(list(map(get_years,rec_dates)))))
    dates={}
    for y in years:
        dates[y]={}
        for m in range(1,13):
            if str(y)+"-"+str(m).zfill(2) in rec_dates:
                dates[y][m]=True
            else:
                dates[y][m]=False
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
    return render(request,'ved/HRKReport.html',context)
