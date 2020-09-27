from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Competitors
from .models import Organisation
from .forms import SearchForm
from django.db.models import Count, Sum, Q

from django.contrib.postgres.aggregates import ArrayAgg


from .models import Records, Organisation, Organization, Trademark

# Create your views here.
def index(request):
    return render(request,'ved/index.html')

def CompetitorsComparse(request):
    competitors = Competitors.objects.all()[:15]
    search_form = SearchForm()
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        search_form = SearchForm(request.POST)
    context = {"competitors": competitors,"search_form": search_form}
    return render(request,'ved/CompetitorsComparse.html',context)

def IndividualReport(request):
    organisation = Organisation.objects.all()[:15]
    search_form = SearchForm()
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
 #       print(request.POST['search_string'])
 #       print(Organisation.objects.filter(edrpou=request.POST['search_string']).query)
        organisation = Organisation.objects.filter(Q(edrpou__startswith=request.POST['search_string']) | Q(name__icontains=request.POST['search_string']))
        search_form = SearchForm(request.POST)
    context = {"organisation": organisation,"search_form": search_form}
    return render(request,'ved/IndividualReport.html',context)

def IndividualReportFirmShow(request,edrpou_num):
    if edrpou_num >= 0:
        
        queryset_list = Records.objects.filter(recipient__edrpou__icontains=edrpou_num)\
                .values('gtd__date', 'gtd__name', 'recipient__name', 'recipient__edrpou').order_by('-gtd__date')\
                .annotate(gtd_count=Count('gtd__name'), total_cost=Sum('gtd__cost_fact'), tms=ArrayAgg('gtd__trademark__name', distinct=True))
        context = {"edrpou_detail": edrpou_num, 'report': queryset_list}
        return render(request,'ved/IndividualReportFirmShow.html',context)
    else:
        return HttpResponse('EDRPOU {0} IS NOT VALID.<br><a href="/">  - Go back</a>'.format(edrpou_num))