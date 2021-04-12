from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.http import is_safe_url,urlunquote
from .models import Profile
from .forms import ProfileForm
import json 
from urllib.request import Request, urlopen
import datetime


from .forms import LoginForm


# Create your views here.
@login_required(login_url='login')
def index(request):
    context=dict()
    context.update({'help_page_id':18})
    return render(request, 'main/index.html',context)

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
                user = User.objects.get(username=alogin)
                user.save()
        
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'main/login.html', context)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required(login_url='login')
@user_passes_test(lambda u: u.profile.nal_part, login_url='/')
def about(request):
    return render(request, 'main/info.html')

@login_required(login_url='login')
def FirmInfo(request,edrpou_num):
    url_string="https://api.youscore.com.ua/v1/companyInfo/"+ str(edrpou_num) +"?apiKey=__1f0900000ebe229bcca6e39128b59d5be1fa2bb7"
    print(url_string)
    req = Request(url_string, headers={'User-Agent': 'Mozilla/5.0'})
    data = urlopen(req).read()
    print(data)
    context={
        'data':data,
    }
    return render(request, 'main/FirmInfo.html', context)

@login_required(login_url='login')
def ProfileUpdate(request):
    context= dict({'ref':request.META.get('HTTP_REFERER')})
    if request.method == 'POST':
        user = User.objects.get(username=request.user.username)
        user.email = request.POST.get('email')
        user.save()
        userProfile=Profile.objects.get(user__username=request.user.username)
        userProfile.bio = request.POST.get('bio')
        userProfile.currency = request.POST.get('currency')
        userProfile.save()
        return HttpResponseRedirect(request.POST.get('ref'))

    return render(request,'main/profile.html',context)