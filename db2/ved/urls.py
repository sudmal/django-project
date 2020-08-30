from django.urls import path
from . import views

urlpatterns = [
    path('vedCompetitorsComparse', views.vedCompetitorsComparse, name = 'vedCompetitorsComparse'),
]
