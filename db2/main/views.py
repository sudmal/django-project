from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,authenticate,logout
from django.urls import reverse
from django.utils.http import is_safe_url,urlunquote
import urllib.request, json 



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
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'main/login.html', context)


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

@login_required(login_url='login')
def about(request):
    return render(request, 'main/info.html')

@login_required(login_url='login')
def FirmInfo(request,edrpou_num):
    url_string="https://api.youscore.com.ua/v1/companyInfo/"+ str(edrpou_num) +"?apiKey=1f0900000ebe229bcca6e39128b59d5be1fa2bb7"
    print(url_string)
    with urllib.request.urlopen(url_string) as url:
        data = json.loads(url.read().decode())
    print(data)

    context={}
    return render(request, 'main/FirmInfo.html', context)