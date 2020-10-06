from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,authenticate,logout
from django.urls import reverse
from django.utils.http import is_safe_url,urlunquote
from django.db.models import Count, Sum, Q, Avg, Subquery, OuterRef, F, FloatField
import json

from .models import Competitors
from .forms import LoginForm


# Create your views here.
@login_required(login_url='login')
def index(request):
    return render(request, 'main/index.html')

def login_user(request):
    context=dict()
    form = LoginForm()
    context.update({
        'LoginForm':form,
    })
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            alogin=form.cleaned_data['login_field']
            apassword=form.cleaned_data['pass_field']
            context.update({
                'LoginForm':form,
                })
            user = authenticate(request,username=alogin,password=apassword)
            if user is not None:
                login (request,user)

            print(alogin)
 #       way=request.META.get('HTTP_REFERER')
 #       print (way)
 #       if way:
 #           way = urlunquote(way)
 #       if not is_safe_url(url=way,allowed_hosts=request.get_host()):
 #           way = reverse('home')
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'main/login.html', context)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required(login_url='login')
def about(request):
    return render(request, 'main/info.html')


def autocompleteModel(request):
    if request.is_ajax():
        q = request.GET.get('term', '').capitalize()
        search_qs = Competitors.objects.filter(Q(competitor_name__icontains=q) | Q(competitor_code__icontains=q))

        results = []
        for r in search_qs:
            results.append(r.competitor_name)
        data = json.dumps(results)
        print(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)