from django.shortcuts import render
from .models import Competitors
from .forms import SearchForm


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
    return render(request,'ved/IndividualReport.html')