from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login,authenticate,logout
from django.urls import reverse
from django.utils.http import is_safe_url,urlunquote

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