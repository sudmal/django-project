from django.shortcuts import render
from .models import Competitors



# Create your views here.
def index(request):
    return render(request,'ved/index.html')

def CompetitorsComparse(request):
    competitors = Competitors.objects.all()
    return render(request,'ved/CompetitorsComparse.html',{"competitors": competitors})

def IndividualReport(request):
    return render(request,'ved/IndividualReport.html')