from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from urllib.parse import unquote
from django.core.paginator import Paginator
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
#@cache_page(60 * 60)
def CompetitorsComparse(request):
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

    comparse = GtdRecords.objects.filter(Q(record__recipient__edrpou__in=Competitors.objects.values_list('competitor_code',flat=True)) & \
        Q(record__date__range=[start_date, end_date] ))\
        .extra(where=["LEFT(product_code::text,8) IN (SELECT LEFT(gcodes,8) from tnved_group)"])\
            .values('record__recipient__edrpou','record__recipient__name')\
                .annotate(count=Count('cost_fact',distinct=True),total_cost=Sum('cost_fact')).order_by('-total_cost')
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
    print(data)
    print(labels)
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
@cache_page(60 * 60)
def IndividualReport(request):
    context=dict()
    search_form = SearchForm()
    rec_dates = getRecDates()
    if request.GET.get('search_string'):
        search_form = SearchForm(request.GET)
        grecords_all = GtdRecords.objects.filter((Q(record__recipient__edrpou__startswith=request.GET.get('search_string')) | \
             Q(record__recipient__name__icontains=request.GET.get('search_string'))) & Q(record__date__range=[request.GET.get('start_date'), request.GET.get('end_date')]))\
                .values('record__recipient__edrpou','record__recipient__name','record__recipient__is_competitor')\
                 .annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'), tms_count=Count('trademark__name',distinct=True),\
                     tms=ArrayAgg('trademark__name', distinct=True)).order_by('-total_cost')
        paginator = Paginator(grecords_all, 10)
        page_number = request.GET.get('page')
        grecords = paginator.get_page(page_number)
        print(page_number)
        context = {
            "search_string": request.GET.get('search_string'),
            "pages": grecords,
            "grecords": grecords.object_list,
            "start_date": request.GET.get('start_date'),
            "end_date": request.GET.get('end_date')
            }
    context.update({"search_form": search_form})
    context.update({'rec_dates': rec_dates})
    return render(request,'ved/IndividualReport.html',context)

@login_required(login_url='login')
@cache_page(60 * 60)
def IndividualReportFirmShow(request,edrpou_num):
    context=dict()
    rec_dates = getRecDates()
    if edrpou_num >= 0:
        queryset_list = GtdRecords.objects.filter((Q(record__recipient__edrpou=edrpou_num) & Q(record__date__range=[request.GET['start_date'], request.GET['end_date']])))\
            .values('record__date','record__gtd_name').order_by('record__date')\
                .annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'),tms=ArrayAgg('trademark__name', distinct=True))
        print(queryset_list.query)
        context = {
            "edrpou_detail": edrpou_num,
            'rec_dates' : rec_dates,
            'report': queryset_list,
            'start_date': request.GET['start_date'], 
            'end_date':request.GET['end_date']
            }
        return render(request,'ved/IndividualReportFirmShow.html',context)
    else:
        return HttpResponse('EDRPOU {0} IS NOT VALID.<br><a href="/">  - Go back</a>'.format(edrpou_num))

@login_required(login_url='login')
@cache_page(60 * 60)
def IndividualReportRaw(request,edrpou_num,gtd_num):

    #  <a class="btn btn-primary font-weight-bold" href="{% url 'ved:IndividualReportRaw' %} row.record__gtd_name|slugify"> {{ row.record__gtd_name }}</a>
    context=dict()
    rec_dates = getRecDates()
    gtd=unquote(gtd_num)
    queryset_list = GtdRecords.objects.filter((Q(record__recipient__edrpou=edrpou_num) & Q(record__gtd_name=gtd)))\
            .values('record__sender__name','record__sender__country__name','record__date','product_code','trademark__name','description','cost_fact').order_by('record__date')
    print(queryset_list.query)
    paginator = Paginator(queryset_list, 10)
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)
    context = {
                'rec_dates' : rec_dates,
                'records': records,
                'gtd': gtd,
                'edrpou_num':edrpou_num,
            }
    return render(request,'ved/IndividualReportRaw.html',context)