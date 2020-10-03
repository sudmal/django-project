from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
#from django.contrib.admin import login,authenticate
from django.urls import reverse

# Create your views here.
def index(request):
    return render(request, 'main/index.html')

def login(request):
    return render(request, 'main/login.html')

def about(request):
    return render(request, 'main/info.html')