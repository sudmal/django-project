from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from urllib.parse import unquote
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Competitors
from .models import Organisation,GtdRecords,Records,Trademark,Sender,Country,TnvedGroup,Exchange
from .forms import SearchForm
from django.db.models import Count, Sum, Q, Avg, Subquery, OuterRef, F, FloatField

from django.contrib.postgres.aggregates import ArrayAgg




@login_required(login_url='login')
def index(request):
    return render(request,'ved/index.html')


@login_required(login_url='login')
def CompetitorsComparse(request):

    comparse = GtdRecords.objects.filter(Q(record__recipient__edrpou__in=Competitors.objects.values_list('competitor_code',flat=True)))\
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
        'labels': labels,
        'data': data,
        'comparse': comparse2}
    return render(request,'ved/CompetitorsComparse.html',context)



@login_required(login_url='login')
def test(request):
    gtdrecords = GtdRecords.objects.filter(trademark__name__icontains='UNOX')
    paginator = Paginator(gtdrecords, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        }
    return render(request,'ved/test.html',context)

@login_required(login_url='login')
def IndividualReport(request):
    context=dict()
    search_form = SearchForm()

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
    return render(request,'ved/IndividualReport.html',context)

@login_required(login_url='login')
def IndividualReportFirmShow(request,edrpou_num):
    context=dict()
    if edrpou_num >= 0:
        queryset_list = GtdRecords.objects.filter((Q(record__recipient__edrpou=edrpou_num) & Q(record__date__range=[request.GET['start_date'], request.GET['end_date']])))\
            .values('record__date','record__gtd_name').order_by('record__date')\
                .annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'),tms=ArrayAgg('trademark__name', distinct=True))
        print(queryset_list.query)
        context = {
            "edrpou_detail": edrpou_num,
            'report': queryset_list,
            'start_date': request.GET['start_date'], 
            'end_date':request.GET['end_date']
            }
        return render(request,'ved/IndividualReportFirmShow.html',context)
    else:
        return HttpResponse('EDRPOU {0} IS NOT VALID.<br><a href="/">  - Go back</a>'.format(edrpou_num))

@login_required(login_url='login')
def IndividualReportRaw(request,edrpou_num,gtd_num):

    #  <a class="btn btn-primary font-weight-bold" href="{% url 'ved:IndividualReportRaw' %} row.record__gtd_name|slugify"> {{ row.record__gtd_name }}</a>
    context=dict()
    gtd=unquote(gtd_num)
    queryset_list = GtdRecords.objects.filter((Q(record__recipient__edrpou=edrpou_num) & Q(record__gtd_name=gtd)))\
            .values('record__sender__name','record__sender__country__name','record__date','product_code','trademark__name','description','cost_fact').order_by('record__date')
    print(queryset_list.query)
    paginator = Paginator(queryset_list, 10)
    page_number = request.GET.get('page')
    records = paginator.get_page(page_number)
    context = {
                'records': records,
                'gtd': gtd,
                'edrpou_num':edrpou_num,
            }
    return render(request,'ved/IndividualReportRaw.html',context)