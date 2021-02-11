from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name = 'home'),
    path('<int:edrpou_num>/', views.ArticlePage, name = 'AtrticlePage'),
]
