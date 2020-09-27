from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Competitors
from .models import Organisation,GtdRecords,Records,Trademark
from .forms import SearchForm
from django.db.models import Count, Sum, Q

from django.contrib.postgres.aggregates import ArrayAgg


# Create your views here.
def index(request):
    return render(request,'ved/index.html')

def CompetitorsComparse(request):
    competitors = Competitors.objects.all()
    search_form = SearchForm()
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        search_form = SearchForm(request.POST)
    context = {"competitors": competitors,"search_form": search_form}
    return render(request,'ved/CompetitorsComparse.html',context)

def test(request):
 #   gtdrecords = GtdRecords.objects.filter()
 #   gtdrecords = GtdRecords.objects.filter(record_id__gtd_name__icontains='UA100620/504321')
    gtdrecords = GtdRecords.objects.filter(trademark__name__icontains='UNOX')
    print(gtdrecords.query)

    return render(request,'ved/test.html',locals())

def IndividualReport(request):
    #organisation = Organisation.objects.all()[:15]
    search_form = SearchForm()
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
 #       print(request.POST['search_string'])
 #       print(Organisation.objects.filter(edrpou=request.POST['search_string']).query)

#    queryset_list = Records.objects.filter(recipient__edrpou__icontains=organization)\
#                .values('gtd__date', 'gtd__name', 'recipient__name', 'recipient__edrpou').order_by('-gtd__date')\
#                .annotate(gtd_count=Count('gtd__name'), total_cost=Sum('gtd__cost_fact'), tms=ArrayAgg('gtd__trademark__name', distinct=True))

        #organisation = Organisation.objects.filter(Q(edrpou__startswith=request.POST['search_string']) | Q(name__icontains=request.POST['search_string']))\
        grecords = GtdRecords.objects.filter(Q(records__organisation__edrpou__startswith=request.POST['search_string']) | Q(records__organisation__edrpou__icontains=request.POST['search_string']))
        #sql_string="SELECT o.edrpou,o.NAME,o.is_competitor,count(cost_fact) AS count,sum(cost_fact) AS summ FROM gtd_records gr LEFT JOIN records r ON gr.record_id=r.id LEFT JOIN organisation o ON r.recipient_id=o.id WHERE o.edrpou :: text LIKE '{0}%' OR o.NAME LIKE '%{0}%' GROUP BY o.edrpou,o.NAME,o.is_competitor ORDER BY summ DESC".format(request.POST['search_string'])
        #print(sql_string)
        #organisation = Organisation.objects.raw(sql_string)
        search_form = SearchForm(request.POST)
    #context = {"organisation": organisation,"search_form": search_form}
    return render(request,'ved/IndividualReport.html',locals())

def IndividualReportFirmShow(request,edrpou_num):
    if edrpou_num >= 0:
        queryset_list = Records.objects.filter(recipient__edrpou__icontains=edrpou_num)\
                .values('gtd__date', 'gtd__name', 'recipient__name', 'recipient__edrpou').order_by('-gtd__date')\
                .annotate(gtd_count=Count('gtd__name'), total_cost=Sum('gtd__cost_fact'), tms=ArrayAgg('gtd__trademark__name', distinct=True))
        context = {"edrpou_detail": edrpou_num, 'report': queryset_list}
        return render(request,'ved/IndividualReportFirmShow.html',context)
    else:
        return HttpResponse('EDRPOU {0} IS NOT VALID.<br><a href="/">  - Go back</a>'.format(edrpou_num))