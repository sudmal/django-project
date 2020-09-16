from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('CompetitorsComparse/', views.CompetitorsComparse, name = 'CompetitorsComparse'),
    path('IndividualReport', views.IndividualReport, name = 'IndividualReport'),
    path('IndividualReportFirmDetail', views.IndividualReportFirmDetail, name = 'IndividualReportFirmDetail'),
]
