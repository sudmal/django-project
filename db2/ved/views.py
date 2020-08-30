from django.shortcuts import render
from django.views.generic.list import ListView
from .models import Competitors

class CompetitorsView(ListView):
    model = Competitors
    template_name = 'ved/CompetitorsComparse.html'
    context_object_name = 'competitors'

# Create your views here.
def index(request):
    return render(request,'ved/index.html')

def CompetitorsComparse(request):
    return render(request,'ved/CompetitorsComparse.html')

def IndividualReport(request):
    return render(request,'ved/IndividualReport.html')