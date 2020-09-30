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
    # gtdrecords = GtdRecords.objects.filter(trademark__name__icontains='UNOX')
    gtdrecords = GtdRecords.objects.filter(trademark__name__icontains='UNOX')
    # print(gtdrecords.query)
    print(type(gtdrecords))
    ddd=3

    return render(request,'ved/test.html',locals())

def IndividualReport(request):
    #organisation = Organisation.objects.all()[:15]
    search_form = SearchForm()
    
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        grecords = GtdRecords.objects.filter(Q(record__recipient__edrpou__startswith=request.POST['search_string']) | Q(record__recipient__name__icontains=request.POST['search_string'])).annotate(count=Count("cost_fact"),total_cost=Sum('cost_fact'))
        search_form = SearchForm(request.POST)
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