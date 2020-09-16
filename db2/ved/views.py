from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import Competitors
from .models import Organisation
from .forms import SearchForm


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
        organisation = Organisation.objects.filter(edrpou__startswith=request.POST['search_string'])
        search_form = SearchForm(request.POST)
    context = {"organisation": organisation,"search_form": search_form}
    return render(request,'ved/IndividualReport.html',context)

def IndividualReportFirmDetail(request):
    if request.method == 'POST':
        edrpou_detail = request.POST['edrpou_detail']
        context = {"edrpou_detail": edrpou_detail}
        queryset_list = Records.objects.filter(recipient__edrpou__icontains=organization)\
                .values('gtd__date', 'gtd__name', 'recipient__name', 'recipient__edrpou').order_by('-gtd__date')\
                .annotate(gtd_count=Count('gtd__name'), total_cost=Sum('gtd__cost_fact'), tms=ArrayAgg('gtd__trademark__name', distinct=True))

        return render(request,'ved/IndividualReportFirmDetail.html',context)
    else:
        return(HttpResponseRedirect(reverse('IndividualReport')))