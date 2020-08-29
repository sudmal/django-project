from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def index(request):
    # Возвращаем запрос плюс имя шаблона в папке templates/appname текущего приложения
    return render(request, 'main/index.html')

def about(request):
    return HttpResponse("about")