from django.urls import path
from . import views


app_name="ved"
urlpatterns = [
    path('', views.index, name = 'index'),
    path('CompetitorsComparse/', views.CompetitorsComparse, name = 'CompetitorsComparse'),
    path('IndividualReport/', views.IndividualReport, name = 'IndividualReport'),
    path('IndividualReport/<int:edrpou_num>/', views.IndividualReportFirmShow, name = 'IndividualReportFirmShow'),
]
